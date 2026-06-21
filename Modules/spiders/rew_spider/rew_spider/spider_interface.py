CONST = {
    "BOT_NAME": "rew_spider",

    "ALLOWED_DOMAINS": ["rew.ca"],

    "START_URL": [
        "https://www.rew.ca/rentals/areas/vancouver-bc"
    ],

    "DEFAULT_MAX_PAGES": 3,

    "ROBOTSTXT_OBEY": False,
    "CONCURRENT_REQUESTS_PER_DOMAIN": 1,
    "DOWNLOAD_DELAY": 3,
    "COOKIES_ENABLED": True,

    "HTTPCACHE_ENABLED": True,
    "HTTPCACHE_EXPIRATION_SECS": 18000,
    "HTTPCACHE_DIR": "rew_spider_cache",
    "HTTPCACHE_IGNORE_HTTP_CODES": [403, 404, 429, 500, 503, 504],
    "HTTPCACHE_STORAGE": "scrapy.extensions.httpcache.FilesystemCacheStorage",

    "FEED_EXPORT_ENCODING": "utf-8",
    "LOG_LEVEL": "INFO",
}