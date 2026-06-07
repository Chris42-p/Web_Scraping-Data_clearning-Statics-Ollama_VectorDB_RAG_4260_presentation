# Scrapy settings for kijiji_spider project
#
# For simplicity, this file contains only settings considered important or
# commonly used. You can find more settings consulting the documentation:
#
#     https://docs.scrapy.org/en/latest/topics/settings.html
#     https://docs.scrapy.org/en/latest/topics/downloader-middleware.html
#     https://docs.scrapy.org/en/latest/topics/spider-middleware.html

BOT_NAME = "kijiji_spider"

SPIDER_MODULES = ["kijiji_spider.spiders"]
NEWSPIDER_MODULE = "kijiji_spider.spiders"

ADDONS = {}

# Rotate User-Agent to avoid bot detection
# Kijiji checks headers — a realistic browser UA is required
USER_AGENT = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
    "AppleWebKit/537.36 (KHTML, like Gecko) "
    "Chrome/120.0.0.0 Safari/537.36"
)

# Obey robots.txt rules
# NOTE: Kijiji blocks scrapers in robots.txt, set False to proceed
ROBOTSTXT_OBEY = False

# Concurrency and throttling — be polite, one request at a time
CONCURRENT_REQUESTS = 1
CONCURRENT_REQUESTS_PER_DOMAIN = 1
DOWNLOAD_DELAY = 2          # base delay between requests (seconds)
RANDOMIZE_DOWNLOAD_DELAY = True  # randomize: 0.5x to 1.5x of DOWNLOAD_DELAY

# Retry on failures — important for Kijiji which may rate-limit
RETRY_TIMES = 3
RETRY_HTTP_CODES = [500, 502, 503, 504, 408, 429]  # 429 = Too Many Requests

# Override the default request headers to look like a real browser
DEFAULT_REQUEST_HEADERS = {
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "en-CA,en;q=0.9",
    "Accept-Encoding": "gzip, deflate, br",
    "Connection": "keep-alive",
    "Upgrade-Insecure-Requests": "1",
}

# Enable downloader middlewares
# See https://docs.scrapy.org/en/latest/topics/downloader-middleware.html
DOWNLOADER_MIDDLEWARES = {
    "kijiji_spider.middlewares.KijijiSpiderDownloaderMiddleware": 543,
}

# Configure item pipelines
# See https://docs.scrapy.org/en/latest/topics/item-pipeline.html
ITEM_PIPELINES = {
    "kijiji_spider.pipelines.KijijiSpiderPipeline": 300,
}

# AutoThrottle — automatically adjusts delay based on server response time
AUTOTHROTTLE_ENABLED = True
AUTOTHROTTLE_START_DELAY = 2
AUTOTHROTTLE_MAX_DELAY = 10
AUTOTHROTTLE_TARGET_CONCURRENCY = 1.0
#AUTOTHROTTLE_DEBUG = False

# HTTP caching — cache responses during development to avoid hitting server
#HTTPCACHE_ENABLED = True
#HTTPCACHE_EXPIRATION_SECS = 3600
#HTTPCACHE_DIR = "httpcache"
#HTTPCACHE_IGNORE_HTTP_CODES = []
#HTTPCACHE_STORAGE = "scrapy.extensions.httpcache.FilesystemCacheStorage"

# Set settings whose default value is deprecated to a future-proof value
FEED_EXPORT_ENCODING = "utf-8"
