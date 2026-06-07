"""
Kijiji Spider Interface

Purpose:
    Stores all hardcoded configuration values for the Kijiji Scrapy spider.
    Following project convention: hardcoded values go in the interface,
    keeping the spider class clean and configurable.

Implementation Notes:
    - BASE_URL: Kijiji root domain
    - START_URL: Vancouver apartments/condos for rent category
    - Location code 1700287 = Vancouver, BC on Kijiji
    - Category code c37 = Apartments & Condos
    - Pagination: /page-N/ inserted before category code
    - Scrapy anti-bot settings stored here, not hardcoded in spider
"""

from abc import ABC, abstractmethod

# == Constants ==
CONST = {
    # URLs
    "BASE_URL": "https://www.kijiji.ca",
    "START_URL": "https://www.kijiji.ca/b-apartments-condos/vancouver/c37l1700287",
    "LOCATION_CODE": "l1700287",        # Vancouver, BC
    "CATEGORY_CODE": "c37",             # Apartments & Condos

    # Scrapy anti-bot settings
    "USER_AGENT": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/120.0.0.0 Safari/537.36"
    ),
    "DELAY_SECONDS": 2,                 # base delay between requests
    "RANDOMIZE_DELAY": True,            # randomize: 0.5x to 1.5x of DELAY_SECONDS
    "RETRY_TIMES": 3,                   # retry on failure
    "RETRY_HTTP_CODES": [500, 502, 503, 504, 408, 429],  # 429 = rate limited
    "CONCURRENT_REQUESTS": 1,           # one request at a time — be polite
    "ROBOTSTXT_OBEY": False,            # Kijiji blocks scrapers in robots.txt
    "DEFAULT_REQUEST_HEADERS": {
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        "Accept-Language": "en-CA,en;q=0.9",
        "Accept-Encoding": "gzip, deflate, br",
        "Connection": "keep-alive",
        "Upgrade-Insecure-Requests": "1",
    },

    # Scraping config
    "DEFAULT_MAX_PAGES": 3,             # default pages to scrape
    "REQUEST_TIMEOUT": 15,              # seconds

    # Geocoding (for map integration)
    "USE_GOOGLE_GEOCODING": False,      # set True to use Google Maps API
    "GOOGLE_MAPS_API_KEY": "",          # add your key here if using Google
    "NOMINATIM_DELAY": 1.1,            # Nominatim rate limit: 1 req/sec

    # Output
    "CSV_OUTPUT_DIR": "scraped_data/",
    "TABLE_NAME": "kijiji_vancouver_rentals",  # DB table name per Chris's convention

    # Error handling
    "ERR_CODE": -1,
    "ERR_TXT": "ERR in KijijiSpider: ",
}


# == Abstract Interface ==
class KijijiSpider_Interface(ABC):
    """
    Interface for Kijiji Scrapy spider.
    Public methods are controller methods callable from frontend or main.py.
    Private methods (__method) handle internal Scrapy logic.
    """

    @abstractmethod
    def run(self, max_pages: int) -> list:
        """
        Public controller — scrape listings from Kijiji Vancouver.
        Internally runs a Scrapy CrawlerProcess.
        Called by frontend or main controller.
        """
        pass

    @abstractmethod
    def export_csv(self, listings: list, output_path: str) -> None:
        """
        Public controller — export scraped listings to CSV.
        """
        pass


class KijijiDetailScraper_Interface(ABC):
    """
    Interface for Kijiji detail page scraper.
    Enriches listings with full address and lat/lng for map integration.
    """

    @abstractmethod
    def scrape(self, url: str) -> dict:
        """
        Public controller — scrape one listing detail page.
        Returns dict with address, latitude, longitude, full_description.
        """
        pass

    @abstractmethod
    def enrich_listings(self, listings: list, delay: float) -> list:
        """
        Public controller — enrich all listings with detail page data.
        Updates address, latitude, longitude on each listing.
        """
        pass
