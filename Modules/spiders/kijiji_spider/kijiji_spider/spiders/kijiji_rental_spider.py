"""
Kijiji Vancouver Rental Spider

Follows cregslist_spider pattern:
- Spider only scrapes, no data processing
- All processing happens in pipelines.py
- Fields match Post_Data from spider_default_obj

Usage:
    cd Modules/spiders/kijiji_spider
    scrapy crawl kijiji_rentals
    scrapy crawl kijiji_rentals -O ../../../scraped_data/kijiji_rentals.csv
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

                # Extract listing ID from URL
                post_id = "N/A"
                if url != "N/A":
                    match = re.search(r"/(\d+)$", url)
                    if match:
                        post_id = match.group(1)

                yield KijijiSpiderItem(
                    post_id=post_id,
                    time_of_post=d.get("datePosted", "N/A"),
                    user_post_title=d.get("name", "N/A"),
                    first_pic=d.get("image", "N/A"),
                    user_meta_tags=str(d.get("keywords", "N/A")),
                    post_url=url,
                    price_of_the_unit=d.get("offers", {}).get("price", "N/A"),
                    num_bedrooms_n_square_feet_sq=str(d.get("numberOfBedrooms", "N/A")),
                    city_general_area=d.get("address", "N/A"),
                    address=d.get("address", "N/A"),
                    bed_and_bath=f"{d.get('numberOfBedrooms', 'N/A')}br / {d.get('numberOfBathroomsTotal', 'N/A')}ba",
                    square_feet_unit=str(d.get("floorSize", {}).get("value", "N/A")),
                    post_description=d.get("description", "N/A"),
                    rent_period="monthly",
                )
                listings_found += 1

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
