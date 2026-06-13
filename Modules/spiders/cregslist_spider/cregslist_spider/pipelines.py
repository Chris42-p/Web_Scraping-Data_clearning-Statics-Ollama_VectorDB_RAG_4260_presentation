# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html




#==== Default imports 
# useful for handling different item types with a single interface
from itemadapter import ItemAdapter
from bs4 import BeautifulSoup
import ollama
from datetime import datetime
from typing import Optional
import json
import sys
import os

#=== internal lib import 
sys.path.append("/home/chris/Desktop/4260_presentation/Modules/spiders") #this is how to import std.obj

from .spider_interface import CONST

from spider_default_obj.spider_default_obj import Post_Data




class CregslistSpiderPipeline:
    def process_item(self, item, spider):
        #metada data           
        post_id=item["post_id"].strip().split(":")[1]
        time_of_post=item["time_of_post"]
        user_post_title=item["user_post_title"]
        first_pic=item['first_pic']
        post_url=item["post_url"]
        
        # user_meta_tags
        user_meta_tags= self.__strip_html(item["user_meta_tags"]).replace("\n"," ")
        user_meta_tags =self.__strip_extra_spaces(user_meta_tags)
          
        #City area .           
        street_number, city, province, postal_code = self.__process_address(item["address"])
        general_area=item["city_general_area"]

        # About the unit
        sqr_feet=item["num_bedrooms_n_square_feet_sq"].split("-")[1]#leaving ft just in case 
        price_of_the_unit=item["price_of_the_unit"]
        rent_period=item["rent_period"]
        post_description=item["post_description"]

        #Bed and bath 
        bed_bath=item["bed_and_bath"]            

        #Square feet 
        square_feet_unit=item["square_feet_unit"]
        square_feet_unit=self.__strip_spaces(self.__strip_html(square_feet_unit))
        square_feet_unit=square_feet_unit[:-1]

        Post_Data(
            post_id,
            time_of_post,
            user_post_title,
            first_pic,
            user_meta_tags, 
            post_url,
            price_of_the_unit,
            sqr_feet,
            general_area,
            street_number,
            city,
            province,
            postal_code,
            bed_bath,
            square_feet_unit,
            post_description,
            rent_period
        ).save_to_db()
        

        # return item
  
 
    def __process_address(self, text):
        if text != None:

            # 'address': '815 SW Marine Dr, Vancouver, BC V6P5Y9', 
            text=text.split(",")
            street_number=text[0]
            city=text[1]
            province=text[2].split(" ")[0]
            postal_code=text[2].split(" ")[1]
        
            return street_number, city, province, postal_code
        else:
            print("This post has a null address")
            return None,None,None,None 

    def __strip_extra_spaces(self, text) :
        text=text.replace("     ",",").replace("   ","") #custom for cregslist prasing of data 
        return text.split(",")
        
    def __strip_spaces(self, text):
        return text.strip()
         
    
    def __strip_html(self,text):
        return BeautifulSoup(text, "html.parser").get_text()
        pass
     
     

#==== ref obj

# yield{ #pass this obj into pipeline .
# #=== meta 
# # -- post ID/PK :
# "post_id": response.css("div.postinginfos >p.postinginfo::text").get(),

# # time of the post: 
# "time_of_post ":response.css("section.body div.reply-button-row p.postinginfo.reveal time::attr(datetime)").get(),
# "user_post_title":response.css("h1.postingtitle  span#titletextonly::text").get(),
# "first_pic":response.css("img::attr(src)").get(),
# "user_meta_tags":response.css("div.attrgroup:nth-child(4) ").get(), # nested attributed, need to process in.py
# "post_url":response.url,

# #== home  
# "price_of_the_unit": response.css("h1.postingtitle  span.price::text").get(),
# "num_bedrooms_n_square_feet_sq": response.css("h1.postingtitle  span.housing::text").get(), #--- process this to, isolate each value
# "city_general_area": response.css("h1.postingtitle .postingtitletext span:last-child::text").get(),
# "address":response.css("h2.street-address::text").get(),                                                #---- process me 
# "bed_and_bath": response.css("div.mapAndAttrs >div.attrgroup span.attr.important:nth-child(1)").get(),  #--- process me 
# "square_feet_unit":response.css("div.mapAndAttrs >div.attrgroup span.attr.important:nth-child(2)").get(),

# #== Amenetirs and living conditions -- LLM process
# "post_description":response.css("section#postingbody").get(),   #---------- make LLM to process this content down. 
# "rent_period": response.css("span.valu > a::text").get(),    
# }