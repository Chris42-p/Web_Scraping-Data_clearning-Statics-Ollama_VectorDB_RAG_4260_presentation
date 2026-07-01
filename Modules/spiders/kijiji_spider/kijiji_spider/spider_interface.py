"""
Kijiji Spider Interface
All hardcoded config values go here — keeping spider/pipeline/settings clean.
Following project convention from cragslist_spider.
"""

from pathlib import Path


CONST = {
    # == Meta
    "BOT_NAME": "kijiji_spider",
    "ALLOWED_DOMAINS": ["kijiji.ca"],
    "START_URL": [
        "https://www.kijiji.ca/b-apartments-condos/vancouver/c37l1700287"
    ],
    "LOCATION_CODE": "l1700287",    # Vancouver, BC
    "CATEGORY_CODE": "c37",         # Apartments & Condos
    "DEFAULT_MAX_PAGES": 3,

    # == Anti-bot settings
    "USER_AGENT": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/120.0.0.0 Safari/537.36"
    ),
    "ROBOTSTXT_OBEY": False,        # Kijiji blocks scrapers in robots.txt
    "CONCURRENT_REQUESTS_PER_DOMAIN": 1,
    "DOWNLOAD_DELAY": 25,
    "RANDOMIZE_DOWNLOAD_DELAY": True,
    "COOKIES_ENABLED": False,
    "RETRY_TIMES": 3,
    "RETRY_HTTP_CODES": [500, 502, 503, 504, 408, 429],
    "DEFAULT_REQUEST_HEADERS": {
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        "Accept-Language": "en-CA,en;q=0.9",
        "Accept-Encoding": "gzip, deflate, br",
        "Connection": "keep-alive",
        "Upgrade-Insecure-Requests": "1",
    },

    # == AutoThrottle
    "AUTOTHROTTLE_ENABLED": True,
    "AUTOTHROTTLE_START_DELAY": 2,
    "AUTOTHROTTLE_MAX_DELAY": 10,
    "AUTOTHROTTLE_TARGET_CONCURRENCY": 1.0,

    # == Caching
    "HTTPCACHE_ENABLED": False,
    "HTTPCACHE_EXPIRATION_SECS": 3600,
    "HTTPCACHE_DIR": "kijiji_spider_cache",
    "HTTPCACHE_IGNORE_HTTP_CODES": [503, 504, 505, 500, 403, 404],
    "HTTPCACHE_STORAGE": "scrapy.extensions.httpcache.FilesystemCacheStorage",

    # == Output
    "FEED_EXPORT_ENCODING": "utf-8",
    "LOG_LEVEL": "INFO",
    "TABLE_NAME": "kijiji_vancouver_rentals",
}


def get_cache_path():
    cache_dir = Path(__file__).parent.parent / "cached" / CONST["BOT_NAME"]
    cache_dir.mkdir(parents=True, exist_ok=True)
    return str(cache_dir)
