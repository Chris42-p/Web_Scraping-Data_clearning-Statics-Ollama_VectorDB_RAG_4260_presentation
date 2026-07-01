#=============== What's the plan 
#get the first page. 
            #parse based on the first page 
            #click next button
            #scrape until we reach the end. 
#=====

#== local imports 
from ..spider_interface import CONST


#==== add ons 
import scrapy
import json


#== IMPORT THE DEFUALT OBJECT DYNAMICALLY =====
from pathlib import Path
import sys

# walk up until we find the folder that contains 'Modules'
current = Path(__file__).resolve()
for parent in current.parents:
    if (parent / "Modules").exists():
        sys.path.append(str(parent))
        break

from Modules.spiders.spider_default_obj.spider_default_obj import Post_Data
#==========================



class CregslistSpiderSpider(scrapy.Spider):
    name = CONST["BOT_NAME"]                     #name of the spider
    allowed_domains = CONST["ALLOWED_DOMAINS"]   #only scrape this page
    start_urls = CONST["START_URL"]        #Need URL of the first post on the website 


    def start_requests(self):  
        for url in self.start_urls:  
            yield scrapy.Request(url, callback=self.parse) # one URL 

    def parse(self, response): #get the result of the first page
        
        for entry in response.css("li.cl-static-search-result"):
            url = entry.css("a::attr(href)").get()
            if url:
                #update when the post was seen again. 
                
                yield scrapy.Request(url, callback=self.parse_page)



    def parse_page(self, response ):  #calls when the response comes back -- what do you want from the page
        #parse pages after first. 
        yield{ #pass this obj into pipeline .
        #=== meta 
        # -- post ID/PK :
        "post_id": response.css("div.postinginfos >p.postinginfo::text").get(),
        "time_of_post":response.css("section.body div.reply-button-row p.postinginfo.reveal time::attr(datetime)").get(),
        "user_post_title":response.css("h1.postingtitle  span#titletextonly::text").get(),
        "first_pic":response.css("img::attr(src)").get(),
        "user_meta_tags":response.css("div.attrgroup:nth-child(4) ").get(), # nested attributed, need to process in.py
        "post_url":response.url,
        "price_of_the_unit": response.css("h1.postingtitle  span.price::text").get(),
        "num_bedrooms_n_square_feet_sq": response.css("h1.postingtitle  span.housing::text").get(), #--- process this to, isolate each value
        "city_general_area": response.css("h1.postingtitle .postingtitletext span:last-child::text").get(),
        "address":response.css("h2.street-address::text").get(),                                                #---- process me 
        "bed_and_bath": response.css("div.mapAndAttrs >div.attrgroup span.attr.important:nth-child(1)").get(),  #--- process me 
        "square_feet_unit":response.css("div.mapAndAttrs >div.attrgroup span.attr.important:nth-child(2)").get(),
        "post_description":response.css("section#postingbody").get(),   #---------- make LLM to process this content down. 
        "rent_period": response.css("span.valu > a::text").get(),    
        }

        #last post return null 





