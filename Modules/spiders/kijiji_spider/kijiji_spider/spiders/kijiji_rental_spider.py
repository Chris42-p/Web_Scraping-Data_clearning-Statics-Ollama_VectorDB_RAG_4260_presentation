"""
Kijiji Vancouver Rental Spider

Two-step scraping:
  1. parse()      - Search results page, get listing URLs from JSON-LD
  2. parse_page() - Detail page, get full data from meta tags + JSON-LD

Follows cregslist_spider pattern:
- Spider only scrapes, no data processing
- All processing happens in pipelines.py
- Fields match Post_Data from spider_default_obj

Usage:
    cd Modules/spiders/kijiji_spider
    scrapy crawl kijiji_spider
"""

import scrapy
import json
import re

from ..spider_interface import CONST
from kijiji_spider.items import KijijiSpiderItem


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

                # Pass basic info from search results to detail page
                meta = {
                    "post_url": url,
                    "user_post_title": d.get("name", "N/A"),
                    "price_of_the_unit": d.get("offers", {}).get("price", "N/A"),
                    "address": d.get("address", "N/A"),
                    "num_bedrooms": str(d.get("numberOfBedrooms", "N/A")),
                    "num_bathrooms": str(d.get("numberOfBathroomsTotal", "N/A")),
                    "square_feet": str(d.get("floorSize", {}).get("value", "N/A")),
                    "first_pic": d.get("image", "N/A"),
                    "pets_allowed": str(d.get("petsAllowed", "N/A")),
                }

                listings_found += 1
                yield scrapy.Request(
                    url=url,
                    callback=self.parse_page,
                    meta=meta,
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
        """Step 2: Detail page — enrich with meta tags and JSON-LD."""
        meta = response.meta

        # Extract listing ID from URL
        post_id = "N/A"
        url = meta.get("post_url", response.url)
        match = re.search(r"/(\d+)$", url)
        if match:
            post_id = match.group(1)

        # == Coordinates from og: meta tags
        latitude = response.css('meta[property="og:latitude"]::attr(content)').get("N/A")
        longitude = response.css('meta[property="og:longitude"]::attr(content)').get("N/A")

        # == Full description from og:description (more complete than JSON-LD snippet)
        full_description = response.css('meta[property="og:description"]::attr(content)').get(
            meta.get("post_url", "N/A")
        )

        # == Time of post from JSON-LD on detail page
        time_of_post = "N/A"
        scripts = response.css('script[type="application/ld+json"]::text').getall()
        for script in scripts:
            try:
                data = json.loads(script)
                if data.get("@type") in ("Product", "Offer", "RentalAction"):
                    time_of_post = data.get("datePosted", "N/A")
                    break
            except json.JSONDecodeError:
                continue

        # == bed/bath string
        num_bedrooms = meta.get("num_bedrooms", "N/A")
        num_bathrooms = meta.get("num_bathrooms", "N/A")
        if num_bedrooms == "0":
            num_bedrooms = "Studio/Bachelor"
        bed_and_bath = f"{num_bedrooms}br / {num_bathrooms}ba"

        yield KijijiSpiderItem(
            post_id=post_id,
            time_of_post=time_of_post,
            user_post_title=meta.get("user_post_title", "N/A"),
            first_pic=meta.get("first_pic", "N/A"),
            user_meta_tags="N/A",
            post_url=url,
            price_of_the_unit=meta.get("price_of_the_unit", "N/A"),
            num_bedrooms_n_square_feet_sq=num_bedrooms,
            city_general_area=meta.get("address", "N/A"),
            address=meta.get("address", "N/A"),
            bed_and_bath=bed_and_bath,
            square_feet_unit=meta.get("square_feet", "N/A"),
            post_description=full_description,
            rent_period="monthly",
            latitude=latitude,     
            longitude=longitude,
        )
