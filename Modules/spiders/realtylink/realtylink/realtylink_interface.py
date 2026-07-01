

CONST={
     #===== DEV DISPLAY TEXT
     "SHOW_TEXT":True,

#== spiders 
     #===== post_status_checker. py 
     "SPIDER_NAME_STATUS_CHECKER":"status_checker",
     
     #===== webpage_scraper .PY
     "SPIDER_NAME_WEB_CRAWLER":"realtylink_spider",
     "ALLOWED_DOMAINS":["realtylink.org"],
     "START_URL":["https://realtylink.org/en/properties~for-rent~vancouver?q=H4sIAAAAAAAACpWRzU7DMBCE38XngCJxgltUCYRAqCIoF8RhiSeNVccOaycQVX131i0_Iafik2f284xs71Rng7pSucrUK_steOU1xBDtm8bUuMN0lEPADfyGqW-nsqUeci7PVEjbyuBd5POLaBDX7QN1XymNsRGchjvVUazbp6lPo1VRFjKO-IiiKnK1H0awWEaLUXsXhk4Omoiz715TFwy6OB9_6L00NgZWh4rsgGPNwbjVvyVjmv0jNPuTQREbz9Ms5xHBaLhoyC7gEtYatznccc67uADX7HtwnFL3jCzfBmJcA0v-npw-lU11a5a_m8H5CczlbMnL7j8BoxVmmR0CAAA&v=2&sortSeed=1953928980&sort=None&pageSize=12&page=1"],



     

#====== SETTINGS      
     #====== Allow duplicates 
     "DUPEFILTER_CLASS":'scrapy.dupefilters.BaseDupeFilter', #turn on duplicate skip to update timestamp 

     #=== general settings
     "ROBOTSTXT_OBEY":False, 
     "CONCURRENT_REQUESTS":1,
     "CONCURRENT_REQUESTS_PER_DOMAIN":1,
     "DOWNLOAD_DELAY":8,
     "COOKIES_ENABLED":False, 
     "AUTOTHROTTLE_ENABLED":False,
     "AUTOTHROTTLE_START_DELAY":5,
     "AUTOTHROTTLE_MAX_DELAY":15,
     "AUTOTHROTTLE_TARGET_CONCURRENCY":1.0,
     "AUTOTHROTTLE_DEBUG":False,

     #====== Cached content. 
     "HTTPCACHE_ENABLED":True, 
     "HTTPCACHE_EXPIRATION_SECS":0,
     "HTTPCACHE_DIR":"httpcache",
     "HTTPCACHE_STORAGE":"scrapy.extensions.httpcache.FilesystemCacheStorage",
     "HTTPCACHE_IGNORE_HTTP_CODES":[503, 504, 505, 500, 403, ],
     "FEED_EXPORT_ENCODING":"UTF-8",

     #===== LOGGING LEVEL 
     "LOG_LEVEL":"DEBUG" #  -- see everything

}