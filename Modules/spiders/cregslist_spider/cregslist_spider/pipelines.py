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
import re

#=== internal lib import 

from .spider_interface import CONST

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


class CregslistSpiderPipeline:
    def process_item(self, item, spider):
        print("\n\n======== GOING TO PARSE THE OBJECT ========\n")
        print(f"{item}\n\n")
        street_number, city, province, postal_code = self.__process_address(item)
        bed, bath=self.get_bed_bath(item)
        
        Post_Data(
            post_id=self.get_post_id(item),
            post_url=self.get_post_url(item),
            time_of_post=self.get_time_of_post(item),
            leasing_agent=self.get_leasing_agent(item),
            general_area=self.get_general_area(item),
            street_number=street_number,
            city=city,
            province=province, 
            postal_code=postal_code,
            price_of_the_unit=self.get_price_of_the_unit(item),
            square_feet_unit=self.get_square_feet_unit(item),
            bed=bed,
            bath=bath,            
            rent_period=self.get_rent_period(item),
            user_post_title=self.get_user_post_title(item),
            user_meta_tags=self.get_user_meta_tags(item),
            post_description=self.get_post_description(item),
            first_img_url=self.get_first_pic(item),
            sqr_feet_lot=None, #not provided by Cregs list
        ).save_new_post_to_db()
        # return item
  
    def get_post_id(self,item):
        if item["post_id"]==None:
            return None

        post_id=item["post_id"].strip().split(":")[1]
        return post_id.strip()

    def get_post_url(self,item):
        if item["post_url"]==None:
            return None

        post_url=item["post_url"]
        return post_url

    def get_time_of_post(self,item):
        if item["time_of_post"]==None:
            return None

        time_of_post=item["time_of_post"]
        return time_of_post

    def get_leasing_agent(self,item):
        leasing_agent="individual"
        return leasing_agent

    def get_general_area(self,item):
        if item["city_general_area"]==None:
            return None
        
        #2  1: cases (vacouver) 2:(1783 West 14th Avenue, Vancouver, BC)

        #case 2 
        try:
            general_area=item["city_general_area"].split(",")[1].strip()
            return general_area
        except:
            general_area=item["city_general_area"].replace("(","").replace(")","")
            return general_area

    def get_price_of_the_unit(self,item):
        if item["price_of_the_unit"]==None:
            return None

        price_of_the_unit=float(item["price_of_the_unit"].replace("$","").replace(",",""))
        return price_of_the_unit
        pass
    
    def get_square_feet_unit(self,item):
        if item["square_feet_unit"]==None:
            return None

        # About the unit
        # sqr_feet=item["num_bedrooms_n_square_feet_sq"].split("-")[1]#leaving ft just in case 

        #Square feet 
        square_feet_unit=item["square_feet_unit"]
        square_feet_unit=self.__strip_spaces(self.__strip_html(square_feet_unit))
        square_feet_unit=int(square_feet_unit[:-1].replace("ft","").replace(",",""))

        return square_feet_unit

    def get_bed_bath(self,item):
        if item["bed_and_bath"]==None:
            return None

        bed_bath=self.__strip_html(item["bed_and_bath"]).strip()
        x=bed_bath.split("/")

        bed=int(re.search(r'\d+',x[0]).group())
        bath=int(re.search(r'\d+',x[1]).group())

        return bed, bath
    
    def get_rent_period(self,item):
        if item["rent_period"]==None:
            return None

        rent_period=item["rent_period"]
        # print(f" \n\n\n{rent_period}")
        return rent_period
    
    def get_user_post_title(self,item):
        if item["user_post_title"]==None:
            return None

        user_post_title=item["user_post_title"]
        return user_post_title

    def get_user_meta_tags(self,item):
        if item["user_meta_tags"]==None:
            return None

        # user_meta_tags
        user_meta_tags= self.__strip_html(item["user_meta_tags"]).replace("\n"," ")
        user_meta_tags =self.__strip_extra_spaces(user_meta_tags)
        return ",".join(user_meta_tags)

    def get_post_description(self,item):
        if item["post_description"]==None:
            return None

        post_description=self.__strip_extra_spaces( self.__strip_html( item["post_description"]))
        return  " ".join(post_description)

    def get_first_pic(self,item):
        if item["first_pic"]==None:
            return None

        first_pic=item['first_pic']
        return first_pic
        pass

    def __process_address(self, item):
        if item["address"] == None:
            return None,None,None,None
        
        text = item["address"].split(",")
        street_number = text[0].strip()
        city          = text[1].strip()
        
        # strip first, then split removes the leading space issue
        province_postal = text[2].strip().split(" ")
        province        = province_postal[0].strip()  # 'BC'
        postal_code     = province_postal[1].strip()  # 'V6J2J7'
        
        return street_number, city, province, postal_code

    def __strip_extra_spaces(self, text) :
        text=text.replace("     ",",").replace("   ","") #custom for cregslist prasing of data 
        return text.split(",")
        
    def __strip_spaces(self, text):
        return text.strip()
         
    def __strip_html(self,text):
        if not text:
            return None
        soup = BeautifulSoup(text, "html.parser")
        # get all text, strip whitespace, filter empty strings
        parts = [t.strip() for t in soup.get_text().split("\n") if t.strip()]
        return ", ".join(parts)
    
