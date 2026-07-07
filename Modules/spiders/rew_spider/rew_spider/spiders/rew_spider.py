import scrapy

from Modules.spiders.rew_spider.rew_spider.spider_interface import CONST
from Modules.spiders.rew_spider.rew_spider.items import RewSpiderItem

from Modules.spiders.rew_spider.rew_spider.rew_parser import (
    extract_price,
    extract_square_feet,
    extract_address,
    format_address,
    split_address,
    build_bed_bath,
    extract_post_id,
    extract_days_on_rew,
    extract_mls_number,
    extract_year_built,
    extract_building_age,
)


class RewSpider(scrapy.Spider):

    name = CONST["BOT_NAME"]
    allowed_domains = CONST["ALLOWED_DOMAINS"]
    start_urls = CONST["START_URL"]

    def __init__(self, max_pages=None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.max_pages = int(max_pages or CONST["DEFAULT_MAX_PAGES"])
        self.visited_pages = set()

    def start_requests(self):
        for url in self.start_urls:
            yield scrapy.Request(
                url=url,
                callback=self.parse,
                errback=self.errback_log,
                meta={"page": 1},
            )

    def parse(self, response):
        current_page = response.meta.get("page", 1)
        self.logger.info(f"REW parse start: page={current_page} url={response.url}")

        if response.url in self.visited_pages:
            self.logger.info(f"Skipping visited page: {response.url}")
            return

        self.visited_pages.add(response.url)

        if response.status in [403, 429]:
            self.logger.warning(
                f"Blocked or rate limited: {response.status} - {response.url}"
            )
            return

        cards = response.css("article")
        self.logger.info(f"Page {current_page}: found {len(cards)} listing cards")

        for idx, card in enumerate(cards, start=1):
            try:
                title = " ".join(
                    text.strip()
                    for text in card.css("::text").getall()
                    if text.strip()
                )

                link = card.css("a::attr(href)").get()
                if not link:
                    self.logger.warning(f"Card {idx}: missing href, skipping")
                    continue

                listing_url = response.urljoin(link)
                formatted_address = format_address(extract_address(title))
                address_parts = split_address(formatted_address) or {}

                self.logger.info(
                    f"Card {idx}: listing_url={listing_url} "
                    f"title={title!r} formatted_address={formatted_address!r} "
                    f"address_parts={address_parts}"
                )

                yield response.follow(
                    listing_url,
                    callback=self.parse_page,
                    errback=self.errback_log,
                    meta={
                        "title": title,
                        "listing_url": listing_url,
                        "formatted_address": formatted_address or "N/A",
                        "street_address": address_parts.get("street_address", "N/A"),
                        "neighbourhood": address_parts.get("neighbourhood", "N/A"),
                        "city": address_parts.get("city", "N/A"),
                        "province": address_parts.get("province", "N/A"),
                        "postal_code": address_parts.get("postal_code", "N/A"),
                        "price": extract_price(title),
                        "square_feet": extract_square_feet(title),
                        "bed_bath": build_bed_bath(title),
                    }
                )
            except Exception:
                self.logger.exception(f"Card {idx}: parse failure on page {response.url}")

        if current_page >= self.max_pages:
            self.logger.info(f"Reached max page limit: {self.max_pages}")
            return

        next_page = response.css("a[rel='next']::attr(href)").get()
        if next_page:
            self.logger.info(f"Following next page: {next_page}")
            yield response.follow(
                next_page,
                callback=self.parse,
                errback=self.errback_log,
                meta={"page": current_page + 1}
            )
        else:
            self.logger.info("No next page found.")

    def errback_log(self, failure):
        self.logger.error("Request failed: %s", failure.request.url if failure.request else "unknown")
        self.logger.error(repr(failure))

    def parse_page(self, response):
        try:
            meta = response.meta
            self.logger.info(
                f"parse_page url={response.url} meta_keys={list(meta.keys())}"
            )

            page_text = response.css("body ::text").getall()
            page_text = " ".join(
                text.strip()
                for text in page_text
                if text.strip()
            )

            latitude = response.css(
                'meta[property="og:latitude"]::attr(content)'
            ).get("N/A")

            longitude = response.css(
                'meta[property="og:longitude"]::attr(content)'
            ).get("N/A")

            first_pic = response.css(
                'meta[property="og:image"]::attr(content)'
            ).get("N/A")

            description = response.css(
                'meta[property="og:description"]::attr(content)'
            ).get("N/A")

            mls_number = extract_mls_number(page_text)
            days_on_rew = extract_days_on_rew(page_text)
            year_built = extract_year_built(page_text)
            building_age = extract_building_age(page_text)

            user_meta_tags = {
                "mls_number": mls_number,
                "days_on_rew": days_on_rew,
                "year_built": year_built,
                "building_age": building_age,
                "latitude": latitude,
                "longitude": longitude,
            }

            self.logger.info(
                f"parsed listing url={response.url} "
                f"mls={mls_number} days_on_rew={days_on_rew}"
            )

            yield RewSpiderItem(
                post_id=mls_number if mls_number != "N/A" else extract_post_id(response.url),
                time_of_post=days_on_rew,
                user_post_title=meta.get("title", "N/A"),
                first_pic=first_pic,
                user_meta_tags=str(user_meta_tags),
                post_url=meta.get("listing_url", response.url),
                price_of_the_unit=meta.get("price", "N/A"),
                num_bedrooms_n_square_feet_sq=meta.get("square_feet", "N/A"),
                city_general_area=meta.get("neighbourhood", "N/A"),
                address=meta.get("formatted_address", "N/A"),
                bed_and_bath=meta.get("bed_bath", "N/A"),
                square_feet_unit=meta.get("square_feet", "N/A"),
                post_description=description,
                rent_period="monthly",
                leasing_agent="REW.ca",
                latitude=latitude,
                longitude=longitude,
            )
        except Exception:
            self.logger.exception(f"parse_page failed for {response.url}")