from pathlib import Path


CONST={
     # realtor_ca_spider.py
     "ALLOWED_DOMAINS":["www.realtylink.org"],
     "START_URL":["https://realtylink.org/en/properties~for-rent~vancouver?q=H4sIAAAAAAAACpWRzU7DMBCE38XngCJxgltUCYRAqCIoF8RhiSeNVccOaycQVX131i0_Iafik2f284xs71Rng7pSucrUK_steOU1xBDtm8bUuMN0lEPADfyGqW-nsqUeci7PVEjbyuBd5POLaBDX7QN1XymNsRGchjvVUazbp6lPo1VRFjKO-IiiKnK1H0awWEaLUXsXhk4Omoiz715TFwy6OB9_6L00NgZWh4rsgGPNwbjVvyVjmv0jNPuTQREbz9Ms5xHBaLhoyC7gEtYatznccc67uADX7HtwnFL3jCzfBmJcA0v-npw-lU11a5a_m8H5CczlbMnL7j8BoxVmmR0CAAA&v=2&sortSeed=1953928980&sort=None&pageSize=12"],
     

     #settings.py
          #== meta
     "BOT_NAME":"realtylink",
     "ROBOTSTXT_OBEY":False,
     "CONCURRENT_REQUESTS_PER_DOMAIN":1,
     "AUTOTHROTTLE_ENABLED":True,
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