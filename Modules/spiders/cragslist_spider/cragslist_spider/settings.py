

from .spider_interface import CONST 

#============

# Scrapy settings for cragslist_spider project
# For simplicity, this file contains only settings considered important or
# commonly used. You can find more settings consulting the documentation:
#
#     https://docs.scrapy.org/en/latest/topics/settings.html
#     https://docs.scrapy.org/en/latest/topics/downloader-middleware.html
#     https://docs.scrapy.org/en/latest/topics/spider-middleware.html

BOT_NAME = CONST["BOT_NAME"]

SPIDER_MODULES = ["Modules.spiders.cragslist_spider.cragslist_spider.spiders"]
NEWSPIDER_MODULE = "Modules.spiders.cragslist_spider.cragslist_spider.spiders"

ADDONS = {}

DUPEFILTER_CLASS = CONST["DUPEFILTER_CLASS"] #enable duplicates 

# Crawl responsibly by identifying yourself (and your website) on the user-agent
#USER_AGENT = "cragslist_spider (+http://www.yourdomain.com)"

# Obey robots.txt rules
ROBOTSTXT_OBEY = CONST["ROBOTSTXT_OBEY"]

# Concurrency and throttling settings
#CONCURRENT_REQUESTS = 16
CONCURRENT_REQUESTS_PER_DOMAIN = CONST["CONCURRENT_REQUESTS_PER_DOMAIN"]
DOWNLOAD_DELAY = CONST["DOWNLOAD_DELAY"]

# Disable cookies (enabled by default)
COOKIES_ENABLED = CONST["COOKIES_ENABLED"]


# Disable Telnet Console (enabled by default)
#TELNETCONSOLE_ENABLED = False

# Override the default request headers:
#DEFAULT_REQUEST_HEADERS = {
#    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
#    "Accept-Language": "en",
#}

# Enable or disable spider middlewares
# See https://docs.scrapy.org/en/latest/topics/spider-middleware.html
#SPIDER_MIDDLEWARES = {
#    "cragslist_spider.middlewares.CregslistSpiderSpiderMiddleware": 543,
#}

# Enable or disable downloader middlewares
# See https://docs.scrapy.org/en/latest/topics/downloader-middleware.html
DOWNLOADER_MIDDLEWARES = {
   "Modules.spiders.cragslist_spider.cragslist_spider.middlewares.UserAgentRotationMilleware": 400,
}

# Enable or disable extensions
# See https://docs.scrapy.org/en/latest/topics/extensions.html
#EXTENSIONS = {
#    "scrapy.extensions.telnet.TelnetConsole": None,
#}

# Configure item pipelines
# See https://docs.scrapy.org/en/latest/topics/item-pipeline.html
ITEM_PIPELINES = {
   'Modules.spiders.cragslist_spider.cragslist_spider.pipelines.CregslistSpiderPipeline': 300
}

# Enable and configure the AutoThrottle extension (disabled by default)
# See https://docs.scrapy.org/en/latest/topics/autothrottle.html
#AUTOTHROTTLE_ENABLED = True
# The initial download delay
#AUTOTHROTTLE_START_DELAY = 5
# The maximum download delay to be set in case of high latencies
#AUTOTHROTTLE_MAX_DELAY = 60
# The average number of requests Scrapy should be sending in parallel to
# each remote server
#AUTOTHROTTLE_TARGET_CONCURRENCY = 1.0
# Enable showing throttling stats for every response received:
#AUTOTHROTTLE_DEBUG = False

# Enable and configure HTTP caching (disabled by default)
# See https://docs.scrapy.org/en/latest/topics/downloader-middleware.html#httpcache-middleware-settings
HTTPCACHE_ENABLED = CONST["HTTPCACHE_ENABLED"]
HTTPCACHE_EXPIRATION_SECS = CONST["HTTPCACHE_EXPIRATION_SECS"]  #5hours --18000 sec 
HTTPCACHE_DIR = CONST["HTTPCACHE_DIR"]
HTTPCACHE_IGNORE_HTTP_CODES = CONST["HTTPCACHE_IGNORE_HTTP_CODES"]
HTTPCACHE_STORAGE = CONST["HTTPCACHE_STORAGE"] 

# Set settings whose default value is deprecated to a future-proof value
FEED_EXPORT_ENCODING =  CONST["FEED_EXPORT_ENCODING"] 



LOG_LEVEL = CONST["LOG_LEVEL"]