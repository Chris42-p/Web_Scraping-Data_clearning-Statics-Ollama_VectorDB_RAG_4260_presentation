this is a spider that's going to scrape realtor.ca rental section 

ref: https://www.realtor.ca/map#view=list&Sort=6-D&GeoIds=g30_c2b2nw3h&GeoName=Vancouver%2C%20BC&PropertyTypeGroupID=1&TransactionTypeId=3&PropertySearchTypeId=1&Currency=CAD


from: cd 4260_presentation/Modules/spiders/realtor_ca
run: scrapy crawl realtor_ca_spider



bots are blocked on this site. 
- used claud to create user header factory 
-
use the following "scrapy shell" method to set user header 
fetch("https://www.realtor.ca/map#view=list&Sort=6-D&GeoIds=g30_c2b2nw3h&GeoName=Vancouver%2C%20BC&PropertyTypeGroupID=1&TransactionTypeId=3&PropertySearchTypeId=1&Currency=CAD", headers={
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
    "Accept-Language": "en-US,en;q=0.9",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
}) # might need to change headers when you use it next time --use: https://useragents.io/random?limit=1500


getting the html response : response.text

