from .spider_interface import CONST
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[4]
LOG_DIR = PROJECT_ROOT / "spider_logs"
LOG_DIR.mkdir(parents=True, exist_ok=True)


BOT_NAME = CONST["BOT_NAME"]

SPIDER_MODULES = ["Modules.spiders.rew_spider.rew_spider.spiders"]
NEWSPIDER_MODULE = "Modules.spiders.rew_spider.rew_spider.spiders"

ROBOTSTXT_OBEY = CONST["ROBOTSTXT_OBEY"]

CONCURRENT_REQUESTS_PER_DOMAIN = CONST["CONCURRENT_REQUESTS_PER_DOMAIN"]
DOWNLOAD_DELAY = CONST["DOWNLOAD_DELAY"]
COOKIES_ENABLED = CONST["COOKIES_ENABLED"]


LOG_ENABLED = True
LOG_LEVEL = "INFO"
LOG_FILE = str(LOG_DIR / "rew_spider.log")
LOG_ENCODING = "utf-8"
LOG_STDOUT = True

ITEM_PIPELINES = {
     "Modules.spiders.rew_spider.rew_spider.pipelines.RewSpiderPipeline": 300,
}

DOWNLOADER_MIDDLEWARES = {
    "Modules.spiders.rew_spider.rew_spider.middlewares.UserAgentRotationMiddleware": 400,
}

HTTPCACHE_ENABLED = CONST["HTTPCACHE_ENABLED"]
HTTPCACHE_EXPIRATION_SECS = CONST["HTTPCACHE_EXPIRATION_SECS"]
HTTPCACHE_DIR = CONST["HTTPCACHE_DIR"]
HTTPCACHE_IGNORE_HTTP_CODES = CONST["HTTPCACHE_IGNORE_HTTP_CODES"]
HTTPCACHE_STORAGE = CONST["HTTPCACHE_STORAGE"]

FEED_EXPORT_ENCODING = CONST["FEED_EXPORT_ENCODING"]
LOG_LEVEL = CONST["LOG_LEVEL"]