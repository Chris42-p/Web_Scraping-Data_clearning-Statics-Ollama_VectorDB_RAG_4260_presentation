import scrapy


#== local imports 
from ..spider_interface import CONST


#==== add ons 
import scrapy
import json
import re

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

class StatusCheckerSpider(scrapy.Spider):
    name = CONST["STATUS_CHECK_NAME"]
    allowed_domains = CONST["ALLOWED_DOMAINS"]
    start_urls = CONST["START_URL"] #place holder else spider wont start
    
    
    def parse(self, response):
        post_=Post_Data()
        rows=post_.get_urls()

        for row in rows: 
            row_id, post_url, scraped_at =row[0],row[1],row[2]

            if "craigslist" not in post_url: #check that the url is for cregslist
                continue

            #send a request to the website 
            yield scrapy.Request(post_url,
                                callback=self.check_status,
                                cb_kwargs={#args into method
                                    "row_id":row_id,
                                    "scraped_at":scraped_at
                                }
                    )   
    


    def check_status(self,response, row_id, scraped_at):
        active_post=None

        #post is expired    ------assuming the post is given a 404
        expired = response.css("blockquote >p::text").get() == 'There is nothing here'
        if expired or response.status == 404:
            self.update_post_status(response.url, status="removed")
            active_post=False
        else:#post is still active
            active_post=True
        
        Post_Data().update_post_last_active(scraped_at,active_post,row_id )

