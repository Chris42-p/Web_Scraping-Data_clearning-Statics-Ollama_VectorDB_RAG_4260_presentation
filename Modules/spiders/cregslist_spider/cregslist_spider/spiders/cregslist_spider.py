import scrapy


class CregslistSpiderSpider(scrapy.Spider):
    name = "cregslist_spider"                       #name of the spider
    allowed_domains = ["vancouver.craigslist.org"]  #only scrape this page
    start_urls = ["https://vancouver.craigslist.org/search/apa#search=2~gallery~0"] #first URL that it should scrpae 

    def start_request(self):
        
        pass

    def parse(self, response):  #calls when the response comes back -- what do you want from the page
        pass

    
