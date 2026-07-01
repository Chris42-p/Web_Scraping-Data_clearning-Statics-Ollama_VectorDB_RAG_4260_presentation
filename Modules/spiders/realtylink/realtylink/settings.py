# Scrapy settings for realtylink project
#
# For simplicity, this file contains only settings considered important or
# commonly used. You can find more settings consulting the documentation:
#
#     https://docs.scrapy.org/en/latest/topics/settings.html
#     https://docs.scrapy.org/en/latest/topics/downloader-middleware.html
#     https://docs.scrapy.org/en/latest/topics/spider-middleware.html

from .realtylink_interface import CONST

BOT_NAME = CONST["SPIDER_NAME_WEB_CRAWLER"]

SPIDER_MODULES = ["Modules.spiders.realtylink.realtylink.spiders"]
NEWSPIDER_MODULE = "Modules.spiders.realtylink.realtylink.spiders"

ADDONS = {}

DUPEFILTER_CLASS = CONST["DUPEFILTER_CLASS"] #enable duplicates 


# Crawl responsibly by identifying yourself (and your website) on the user-agent
#USER_AGENT = "realtylink (+http://www.yourdomain.com)"

# Obey robots.txt rules
ROBOTSTXT_OBEY = CONST["ROBOTSTXT_OBEY"]

# Concurrency and throttling settings
CONCURRENT_REQUESTS = CONST["CONCURRENT_REQUESTS"]
CONCURRENT_REQUESTS_PER_DOMAIN = CONST["CONCURRENT_REQUESTS_PER_DOMAIN"]
DOWNLOAD_DELAY =CONST["DOWNLOAD_DELAY"] 

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
#    "realtylink.middlewares.RealtylinkSpiderMiddleware": 543,
#}

# Enable or disable downloader middlewares
# See https://docs.scrapy.org/en/latest/topics/downloader-middleware.html
DOWNLOADER_MIDDLEWARES = {
   "Modules.spiders.realtylink.realtylink.middlewares.UserAgentRotationMilleware": 300,
}

# Enable or disable extensions
# See https://docs.scrapy.org/en/latest/topics/extensions.html
#EXTENSIONS = {
#    "scrapy.extensions.telnet.TelnetConsole": None,
#}

# Configure item pipelines
# See https://docs.scrapy.org/en/latest/topics/item-pipeline.html
ITEM_PIPELINES = { #item pipeline after downloader millerware. 
   "Modules.spiders.realtylink.realtylink.pipelines.RealtylinkPipeline": 305,
}

# Enable and configure the AutoThrottle extension (disabled by default)
# See https://docs.scrapy.org/en/latest/topics/autothrottle.html
AUTOTHROTTLE_ENABLED = CONST["AUTOTHROTTLE_ENABLED"]
# The initial download delay
AUTOTHROTTLE_START_DELAY = CONST["AUTOTHROTTLE_START_DELAY"]
# The maximum download delay to be set in case of high latencies
AUTOTHROTTLE_MAX_DELAY =CONST["AUTOTHROTTLE_MAX_DELAY"] 
# The average number of requests Scrapy should be sending in parallel to
# each remote server
AUTOTHROTTLE_TARGET_CONCURRENCY = CONST["AUTOTHROTTLE_TARGET_CONCURRENCY"] 
# Enable showing throttling stats for every response received:
AUTOTHROTTLE_DEBUG =CONST["AUTOTHROTTLE_DEBUG"] 

# Enable and configure HTTP caching (disabled by default)
# See https://docs.scrapy.org/en/latest/topics/downloader-middleware.html#httpcache-middleware-settings
HTTPCACHE_ENABLED = CONST["HTTPCACHE_ENABLED"]
HTTPCACHE_EXPIRATION_SECS = CONST["HTTPCACHE_EXPIRATION_SECS"]
HTTPCACHE_DIR = CONST["HTTPCACHE_DIR"]
HTTPCACHE_IGNORE_HTTP_CODES = CONST["HTTPCACHE_IGNORE_HTTP_CODES"]
HTTPCACHE_STORAGE = CONST["HTTPCACHE_STORAGE"]

# Set settings whose default value is deprecated to a future-proof value
FEED_EXPORT_ENCODING = CONST["FEED_EXPORT_ENCODING"]

#LOG LEVEL 
LOG_LEVEL = CONST["LOG_LEVEL"]
