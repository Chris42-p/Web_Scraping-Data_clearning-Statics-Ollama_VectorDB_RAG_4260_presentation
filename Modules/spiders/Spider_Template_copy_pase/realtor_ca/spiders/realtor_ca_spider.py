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

        #this is the cards with data. 
        x=response.css("body div#BodyContenCon div.fullWidth div#listCon div#listInnerCon div") #.len    #this is the divs 
            #loop me:  x= response.css("body div#BodyContenCon div.fullWidth div#listCon div#listInnerCon div").get(1) #cycle this

        href__to_post= response.css("body div#BodyContenCon div.fullWidth div#listCon div#listInnerCon div a.blockLink.listingDetailsLink ").get(1)  ## not done stuck -- got it down to the <div> object but cant open object



        





        pass
    
    def __parse_page(self, item):
        pass



