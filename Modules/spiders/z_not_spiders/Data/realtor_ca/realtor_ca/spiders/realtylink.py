#== sys level imports
import scrapy
import sys
import os 


#==== Local imports 
from ..spider_interface import CONST

sys.path.append("/home/chris/Desktop/4260_presentation/Modules/spiders") #this is how to import std.obj


# calling the spider: scrapy crawl realtor_ca_spider


class RealtorCaSpiderSpider(scrapy.Spider):
    name = CONST["BOT_NAME"]
    allowed_domains = CONST["ALLOWED_DOMAINS"] 
    start_urls = CONST["START_URL"]

    def parse(self, response):
        print(response)

        pass
    
    def __parse_page(self, item):
        pass



