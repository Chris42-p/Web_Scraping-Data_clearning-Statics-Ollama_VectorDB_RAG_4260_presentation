import scrapy

from ..spider_interface import CONST
from ..items import RewSpiderItem

from ..rew_parser import (
    extract_price,
    extract_square_feet,
    extract_address,
    format_address,
    split_address,
    build_bed_bath,
    extract_post_id,
)


class RewSpider(scrapy.Spider):

    name = CONST["BOT_NAME"]
    allowed_domains = CONST["ALLOWED_DOMAINS"]
    start_urls = CONST["START_URL"]

    def start_requests(self):
        for url in self.start_urls:
            yield scrapy.Request(
                url=url,
                callback=self.parse,
                meta={"page": 1}
            )

    def parse(self, response):

        cards = response.css("article")

        self.logger.info(
            f"Found {len(cards)} listing cards"
        )

        for card in cards:

            title = " ".join(
                text.strip()
                for text in card.css("::text").getall()
                if text.strip()
            )

            link = card.css("a::attr(href)").get()

            if not link:
                continue

            listing_url = response.urljoin(link)

            formatted_address = format_address(
                extract_address(title)
            )

            address_parts = split_address(
                formatted_address
            )

            yield response.follow(
                listing_url,
                callback=self.parse_page,
                meta={
                    "title": title,
                    "listing_url": listing_url,
                    "formatted_address": formatted_address,
                    "address_parts": address_parts,
                }
            )

    def parse_page(self, response):

        meta = response.meta

        description = response.css(
            'meta[property="og:description"]::attr(content)'
        ).get("N/A")

        first_pic = response.css(
            'meta[property="og:image"]::attr(content)'
        ).get("N/A")

        latitude = response.css(
            'meta[property="og:latitude"]::attr(content)'
        ).get("N/A")

        longitude = response.css(
            'meta[property="og:longitude"]::attr(content)'
        ).get("N/A")

        title = meta["title"]

        yield RewSpiderItem(

            post_id=extract_post_id(
                meta["listing_url"]
            ),

            time_of_post="N/A",

            user_post_title=title,

            first_pic=first_pic,

            user_meta_tags="N/A",

            post_url=meta["listing_url"],

            price_of_the_unit=extract_price(title),

            num_bedrooms_n_square_feet_sq=extract_square_feet(title),

            city_general_area=meta["address_parts"]["neighbourhood"],

            address=meta["formatted_address"],

            bed_and_bath=build_bed_bath(title),

            square_feet_unit=extract_square_feet(title),

            post_description=description,

            rent_period="monthly",

            leasing_agent="REW.ca",

            latitude=latitude,

            longitude=longitude,
        )