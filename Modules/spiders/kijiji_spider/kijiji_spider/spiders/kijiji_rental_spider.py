"""
Kijiji Vancouver Rental Spider

Two-step scraping:
  1. parse()      - Search results page, get listing URLs from JSON-LD
  2. parse_page() - Detail page, parse __NEXT_DATA__ (Next.js Apollo state)
                     for complete and reliable listing data, including the
                     full address (search-page JSON-LD only gives a rough
                     neighbourhood-level address, which caused missing
                     street numbers).

Follows cregslist_spider pattern:
- Spider only scrapes, no data processing
- All processing happens in pipelines.py
- Fields match Post_Data from spider_default_obj

TODO: Add check_status / re-scrape detection logic once Chris updates
      Post_Data.__init__() to not require all 19 fields upfront.
      (get_record_by_url and update_post_last_active should be callable
       without constructing a full listing object first.)

Usage:
    cd Modules/spiders/kijiji_spider
    scrapy crawl kijiji_spider
"""

import scrapy
import json
import re

from ..spider_interface import CONST
from ..items import KijijiSpiderItem


class KijijiRentalsSpider(scrapy.Spider):

    name = CONST["BOT_NAME"]
    allowed_domains = CONST["ALLOWED_DOMAINS"]
    start_urls = CONST["START_URL"]

    def __init__(self, max_pages=None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.max_pages = int(max_pages or CONST["DEFAULT_MAX_PAGES"])
        self.current_page = 1

    def start_requests(self):
        for url in self.start_urls:
            yield scrapy.Request(url, callback=self.parse)

    def parse(self, response):
        """Step 1: Search results page — get listing URLs from JSON-LD."""
        scripts = response.css('script[type="application/ld+json"]::text').getall()
        listings_found = 0

        for script in scripts:
            try:
                data = json.loads(script)
            except json.JSONDecodeError:
                continue

            if data.get("@type") != "ItemList":
                continue

            items = data.get("itemListElement", [])
            self.logger.info(f"Page {self.current_page}: found {len(items)} listings")

            for entry in items:
                d = entry.get("item", {})
                url = d.get("url", "N/A")

                if url == "N/A":
                    continue

                listings_found += 1
                yield scrapy.Request(
                    url=url,
                    callback=self.parse_page,
                    meta={"post_url": url},
                    headers={"Referer": response.url},
                )

        # Pagination
        if self.current_page < self.max_pages and listings_found > 0:
            self.current_page += 1
            next_url = (
                f"https://www.kijiji.ca/b-apartments-condos/vancouver/"
                f"page-{self.current_page}/c37l1700287"
            )
            yield scrapy.Request(
                url=next_url,
                callback=self.parse,
                headers={"Referer": response.url},
            )

    def parse_page(self, response):
        """
        Step 2: Detail page — parse __NEXT_DATA__ (Apollo state) for
        complete, reliable listing data including full address.
        """
        meta = response.meta
        url = meta.get("post_url", response.url)

        post_id = "N/A"
        match = re.search(r"/(\d+)$", url)
        if match:
            post_id = match.group(1)

        listing = self.__get_listing_from_next_data(response, post_id)

        if listing is None:
            self.logger.warning(f"Could not find __NEXT_DATA__ listing for {url}")
            return

        # == location — full address from Apollo state
        location = listing.get("location", {}) or {}
        address = location.get("address", "N/A")
        coordinates = location.get("coordinates", {}) or {}
        latitude = coordinates.get("latitude", "N/A")
        longitude = coordinates.get("longitude", "N/A")
        city_name = location.get("name", "N/A")

        # == price
        price_obj = listing.get("price", {}) or {}
        price = price_obj.get("amount", "N/A")

        # == title / description
        user_post_title = listing.get("title", "N/A")
        post_description = listing.get("description", "N/A")

        # == time of post
        time_of_post = listing.get("activationDate", "N/A")

        # == images
        image_urls = listing.get("imageUrls", []) or []
        first_pic = image_urls[0] if image_urls else "N/A"

        # == attributes (bedrooms, bathrooms, sqft, etc.)
        attrs = self.__parse_attributes(listing)
        num_bedrooms = attrs.get("numberbedrooms", attrs.get("bedrooms", "N/A"))
        num_bathrooms = attrs.get("numberbathrooms", attrs.get("bathrooms", "N/A"))
        square_feet = attrs.get("areainfeet", attrs.get("size", "N/A"))

        if num_bedrooms in ("0", 0):
            num_bedrooms = "Studio/Bachelor"
        bed_and_bath = f"{num_bedrooms}br / {num_bathrooms}ba"

        # == leasing agent — from posterInfo
        poster_info = listing.get("posterInfo", {}) or {}
        agent_phone = poster_info.get("phoneNumber", "N/A")
        agent_website = poster_info.get("websiteUrl", "N/A")
        leasing_agent = f"{agent_website} | {agent_phone}" if agent_website != "N/A" else agent_phone

        # == lot size — not available on Kijiji rental listings
        sqr_feet_lot = "N/A"

        yield KijijiSpiderItem(
            post_id=post_id,
            time_of_post=time_of_post,
            user_post_title=user_post_title,
            first_pic=first_pic,
            user_meta_tags="N/A",
            post_url=url,
            price_of_the_unit=price,
            num_bedrooms_n_square_feet_sq=num_bedrooms,
            city_general_area=city_name,
            address=address,
            bed_and_bath=bed_and_bath,
            square_feet_unit=square_feet,
            post_description=post_description,
            rent_period="monthly",
            latitude=latitude,
            longitude=longitude,
            leasing_agent=leasing_agent,
            sqr_feet_lot=sqr_feet_lot,
        )

    def check_status(self, response, row_id, scraped_at):
        """
        Lightweight re-scrape: check if a previously-seen listing is
        still active, and update its last-active timestamp.

        A removed/expired Kijiji listing returns the page but with a
        "There is nothing here" style message, or a 404 status.
        """
        post_data = self.__get_post_data_class()
        if post_data is None:
            return

        removed_text = response.css('body::text').re_first(r"[Tt]here is nothing here") or ""
        is_removed = bool(removed_text) or response.status == 404

        active_post = not is_removed

        post_data.update_post_last_active(
            scraped_at=scraped_at,
            active_post=active_post,
            row_id=row_id,
        )

        self.logger.info(
            f"[check_status] row_id={row_id} active={active_post} url={response.url}"
        )

    def __check_existing_record(self, url: str):
        """
        Looks up whether this listing URL is already in the DB.
        Returns (row_id, scraped_at) if found, else None.
        """
        post_data = self.__get_post_data_class()
        if post_data is None:
            return None

        record = post_data.get_record_by_url(url)
        if not record:
            return None

        # record is [row_id, address] per spider_default_obj.py —
        # scraped_at isn't returned by this query, so we re-derive it
        # at check time inside update_post_last_active instead.
        row_id = record[0]
        scraped_at = None
        return row_id, scraped_at

    def __get_post_data_class(self):
        """Lazily imports Post_Data to avoid breaking spider startup
        if the module path isn't resolvable in this environment."""
        try:
            from pathlib import Path
            import sys
            current = Path(__file__).resolve()
            for parent in current.parents:
                if (parent / "Modules").exists():
                    sys.path.append(str(parent))
                    break
            from Modules.spiders.spider_default_obj.spider_default_obj import Post_Data
            return Post_Data
        except Exception as e:
            self.logger.warning(f"Could not import Post_Data: {e}")
            return None

    # ------------------------------------------------------------------ #
    #  __NEXT_DATA__ / Apollo state helpers
    # ------------------------------------------------------------------ #

    def __get_listing_from_next_data(self, response, post_id: str) -> dict | None:
        """
        Parses the __NEXT_DATA__ script tag and pulls out the
        RealEstateListing:{post_id} object from the Apollo cache.
        """
        next_data_raw = response.css('script#__NEXT_DATA__::text').get()
        if not next_data_raw:
            return None

        try:
            next_data = json.loads(next_data_raw)
        except json.JSONDecodeError:
            return None

        apollo_state = (
            next_data.get("props", {})
            .get("pageProps", {})
            .get("__APOLLO_STATE__", {})
        )

        listing_key = f"RealEstateListing:{post_id}"
        return apollo_state.get(listing_key)

    def __parse_attributes(self, listing: dict) -> dict:
        """
        Flattens the listing's attributes.all list (machineKey -> value)
        into a simple lowercase-keyed dict for easy lookup.
        """
        flat = {}
        attrs = listing.get("attributes", {}) or {}
        for attr in attrs.get("all", []) or []:
            key = (attr.get("machineKey") or "").lower()
            values = attr.get("values") or attr.get("value")
            if isinstance(values, list):
                flat[key] = values[0] if values else "N/A"
            elif values is not None:
                flat[key] = values
        return flat