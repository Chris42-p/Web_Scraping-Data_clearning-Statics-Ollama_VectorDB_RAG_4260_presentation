this is the implementation notes for realtylink


fetch the website: 

## base website

fetch("https://realtylink.org/en/properties~for-rent~vancouver?q=H4sIAAAAAAAACpWRzU7DMBCE38XngCJxgltUCYRAqCIoF8RhiSeNVccOaycQVX131i0_Iafik2f284xs71Rng7pSucrUK_steOU1xBDtm8bUuMN0lEPADfyGqW-nsqUeci7PVEjbyuBd5POLaBDX7QN1XymNsRGchjvVUazbp6lPo1VRFjKO-IiiKnK1H0awWEaLUXsXhk4Omoiz715TFwy6OB9_6L00NgZWh4rsgGPNwbjVvyVjmv0jNPuTQREbz9Ms5xHBaLhoyC7gEtYatznccc67uADX7HtwnFL3jCzfBmJcA0v-npw-lU11a5a_m8H5CczlbMnL7j8BoxVmmR0CAAA&v=2&sortSeed=1953928980&sort=None&pageSize=12", headers={
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.116 Safari/537.36 OPR/69.0.3686.57",
    "Accept-Language": "en-US,en;q=0.9",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
}) # might need to change headers when you use it next time --use: https://useragents.io/random?limit=1500


## instance website 
fetch(
     "https://realtylink.org/en/properties~for-rent~vancouver?q=H4sIAAAAAAAACpWRzU7DMBCE38XngCJxgltUCYRAqCIoF8RhiSeNVccOaycQVX131i0_Iafik2f284xs71Rng7pSucrUK_steOU1xBDtm8bUuMN0lEPADfyGqW-nsqUeci7PVEjbyuBd5POLaBDX7QN1XymNsRGchjvVUazbp6lPo1VRFjKO-IiiKnK1H0awWEaLUXsXhk4Omoiz715TFwy6OB9_6L00NgZWh4rsgGPNwbjVvyVjmv0jNPuTQREbz9Ms5xHBaLhoyC7gEtYatznccc67uADX7HtwnFL3jCzfBmJcA0v-npw-lU11a5a_m8H5CczlbMnL7j8BoxVmmR0CAAA&v=2&sortSeed=1953928980&sort=None&pageSize=12&page=2",
 headers={
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.116 Safari/537.36 OPR/69.0.3686.57",
    "Accept-Language": "en-US,en;q=0.9",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
}) 
#### might need to change headers when you use it next time --use: https://useragents.io/random?limit=1500



## fetch a card 
fetch(
    "https://realtylink.org/en/apartment~for-rent~vancouver/263099040",
 headers={
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.116 Safari/537.36 OPR/69.0.3686.57",
    "Accept-Language": "en-US,en;q=0.9",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
})



## see all results. 



# create a scrapy spider:  scrapy genspider status_checker "https://realtylink.org/en/apartment~for-rent~vancouver?listingnotfound=363162355&q=H4sIAAAAAAAACmWPQUvEMBCF_0vOVRa8eSs9iAgiVvay7GFMX9vBNAmTtBKW_nen7Arrepv33veGmZOZXDKPZmcq8ynhC9KEDmqoDn3PFi8oZzknPCEMQnEs7UgR2ttVJm3jnvGt8nBUDRI7vtJ02dKzy5BL2DNcl_bk5q19OJ2N507RhjKGIEUry5ar9Y7EHXxmcmatruEWzrEfPkrEH97nG_BNQoTkckPWkSRP__GmbusrzAaf5kmv54y73-fZ1gJ6uF_I2zAvELMe1x80wRVsSAEAAA&sortSeed=410379507&sort=DateDesc&pageSize=12"


## change to the right directory 
1) cd 4260_presentation/Modules/spiders/realtylink

## running the spider 
2) scrapy crawl realtylink_spider

## running the checker. 
3) scrapy crawl status_checker





