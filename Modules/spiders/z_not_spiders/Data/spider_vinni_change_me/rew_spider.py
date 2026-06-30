
import scrapy

from ..rew_parser import parse_rew_rental_listing

class REWSpider(scrapy.Spider):
    """
    Scrapy spider for collecting real estate listings from REW.ca.
    """

    name = "rew_spider"

    visited_pages = set()
    max_pages = 20

    custom_settings = {
        "ROBOTSTXT_OBEY": False,
        "COOKIES_ENABLED": True,

        "DOWNLOAD_DELAY": 2,
        "AUTOTHROTTLE_ENABLED": True,
        "AUTOTHROTTLE_START_DELAY": 2,
        "AUTOTHROTTLE_MAX_DELAY": 10,

        "RETRY_ENABLED": True,
        "RETRY_TIMES": 3,

        "HTTPERROR_ALLOWED_CODES": [403, 429],

        "LOG_LEVEL": "INFO",

        "USER_AGENT": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/137.0.0.0 Safari/537.36",
        "ROBOTSTXT_OBEY": False,
        "DEFAULT_REQUEST_HEADERS": {
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.9",
        },

        "DEFAULT_REQUEST_HEADERS": {
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
            "Accept-Language": "en-US,en;q=0.9",
            "Referer": "https://www.rew.ca/",
        },

        "ITEM_PIPELINES": {
            "Modules.spiders.Data.spider_vinni_change_me.pipelines.SQLitePipeline": 300,
        },

    }

    start_urls = [
        "https://www.rew.ca/rentals/areas/vancouver-bc"
    ]

    def parse(self, response):

        current_page = response.meta.get("page", 1)

        if response.url in self.visited_pages:
            self.logger.info(f"Skipping already visited page: {response.url}")
            return

        self.visited_pages.add(response.url)

        if response.status in [403, 429]:
            self.logger.warning(
                f"Blocked or rate limited: {response.status} - {response.url}"
            )
            return

        cards = response.css("article")

        self.logger.info(
            f"Found {len(cards)} listing cards on page {current_page}"
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

            yield parse_rew_rental_listing(title, listing_url)

        if current_page >= self.max_pages:
            self.logger.info(
                f"Reached max page limit: {self.max_pages}"
            )
            return

        next_page = response.css("a[rel='next']::attr(href)").get()

        if next_page:
            yield response.follow(
                next_page,
                callback=self.parse,
                meta={"page": current_page + 1}
            )
        else:
            self.logger.info("No next page found. Scraping finished.")