from pathlib import Path



CONST={
     "HTTPCACHE_DIR": "cregslist_spider_cache", #set this one dynamically #get_cache_path(),
     # cregslist_spider.py
     "ALLOWED_DOMAINS":["vancouver.craigslist.org"],
     "START_URL":["https://vancouver.craigslist.org/search/hhh?excats=2-16-1-20-1-1-17-7-34-22-22-1#search=2~gallery~0"],
     

     #settings.py
          #== meta
     "BOT_NAME":"cregslist_spider",
     "ROBOTSTXT_OBEY":True,
     "CONCURRENT_REQUESTS_PER_DOMAIN":1,
     "DOWNLOAD_DELAY": 30,  #sec #slow it down for LLM to process obj
     "COOKIES_ENABLED":False, 
          #== caching. 
     "HTTPCACHE_ENABLED":True, 
     "HTTPCACHE_EXPIRATION_SECS":18000,
     "HTTPCACHE_DIR": "~/Desktop/4260_presentation/httpcache",
     "HTTPCACHE_IGNORE_HTTP_CODES":[503, 504, 505, 500, 403, 404],
     "HTTPCACHE_STORAGE": "scrapy.extensions.httpcache.FilesystemCacheStorage",
     "FEED_EXPORT_ENCODING":"utf-8",
     "LOG_LEVEL":"DEBUG",


}


def get_cache_path():
    cache_dir = Path(__file__).parent.parent / "cached" / CONST["BOT_NAME"]
    cache_dir.mkdir(parents=True, exist_ok=True)
    return str(cache_dir)