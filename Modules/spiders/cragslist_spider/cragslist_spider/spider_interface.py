from pathlib import Path



CONST={
     #==== dev 
     "DISPLAY_TEXT":True,
     
     #=== status checker spider. 
     "STATUS_CHECK_NAME":"status_checker",   


     #==== spider.py
     "HTTPCACHE_DIR": "cregslist_spider_cache", #set this one dynamically #get_cache_path(),
     # cregslist_spider.py
     "ALLOWED_DOMAINS":["craigslist.org"],
     "START_URL":["https://www.craigslist.org/search/subarea/van?cat=hhh"],

     #settings.py
          #== duplicate 
     "DUPEFILTER_CLASS":'scrapy.dupefilters.BaseDupeFilter', #turn on duplicate skip to update timestamp 
          #== meta
     "BOT_NAME":"cragslist_spider",
     "ROBOTSTXT_OBEY":False,
     "CONCURRENT_REQUESTS_PER_DOMAIN":1,
     "DOWNLOAD_DELAY": 8,  #sec #slow it down for LLM to process obj
     "COOKIES_ENABLED":False, 
          #== caching. 
     "HTTPCACHE_ENABLED":True, 
     "HTTPCACHE_EXPIRATION_SECS":1,
     "HTTPCACHE_DIR": "~/Desktop/4260_presentation/httpcache",
     "HTTPCACHE_IGNORE_HTTP_CODES":[503, 504, 505, 500, 403, 301], #need 404 to know when to update post
     "HTTPCACHE_STORAGE": "scrapy.extensions.httpcache.FilesystemCacheStorage",
     "FEED_EXPORT_ENCODING":"utf-8",
     "LOG_LEVEL":"DEBUG",


}


def get_cache_path():
    cache_dir = Path(__file__).parent.parent / "cached" / CONST["BOT_NAME"]
    cache_dir.mkdir(parents=True, exist_ok=True)
    return str(cache_dir)