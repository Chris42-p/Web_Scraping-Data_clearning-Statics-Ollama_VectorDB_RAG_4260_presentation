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
import time

#=== internal lib import 

from .spider_interface import CONST
from geopy.geocoders import Nominatim

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
    @classmethod
    def from_crawler(cls, crawler):
        pipe = cls()
        pipe.crawler = crawler
        return pipe

    def process_item(self, item):
        if CONST["DISPLAY_TEXT"]:
            try:
                safe_preview = str(item).encode("utf-8", errors="replace").decode("utf-8")
                print("\n\n======== GOING TO PARSE THE OBJECT ========\n")
                print(f"{safe_preview[:1500]}\n")
            except Exception:
                print("\n\n======== GOING TO PARSE THE OBJECT ========\n")

        street_number, city, province, postal_code = self.__process_address(item)
        bed, bath = self.get_bed_bath(item)

        latitude, longitude, address_osm = self.__geocode_address(
            street_number,
            city,
            province,
            postal_code,
        )

        spider = getattr(self.crawler, "spider", None)
        source_spider = spider.name if spider else "craigslist"

        post = Post_Data(
            post_id=self.get_post_id(item),
            time_of_post=self.get_time_of_post(item),
            user_post_title=self.get_user_post_title(item),
            first_pic=self.get_first_pic(item),
            user_meta_tags=self.get_user_meta_tags(item),
            post_url=self.get_post_url(item),
            price_of_the_unit=self.get_price_of_the_unit(item),
            sqr_feet=None,
            general_area=self.get_general_area(item),
            street_number=street_number,
            city=city,
            province=province,
            postal_code=postal_code,
            latitude=latitude,
            longitude=longitude,
            address_osm=address_osm,
            bed=bed,
            bath=bath,
            square_feet_unit=self.get_square_feet_unit(item),
            post_description=self.get_post_description(item),
            rent_period=self.get_rent_period(item),
            leasing_agent=self.get_leasing_agent(item),
            source_spider=source_spider,
            img_url=self.get_first_pic(item),
        )

        post.save_new_post_to_db()
        return item


    def __geocode_address(self, street_number, city, province, postal_code):
        if not street_number or not city:
            return None, None, None

        parts = [street_number, city, province, postal_code, "Canada"]
        query = ", ".join([part for part in parts if part and part != "N/A"])

        try:
            geolocator = Nominatim(user_agent="housing_scraper_geocoder")
            location = geolocator.geocode(query, timeout=10)
            time.sleep(1)

            if not location:
                return None, None, None

            return float(location.latitude), float(location.longitude), location.address
        except Exception as exc:
            print(f"Geocode failed for '{query}': {exc}")
            return None, None, None
  
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
        digits = "".join(ch for ch in square_feet_unit if ch.isdigit())
        if not digits:
            return None

        return int(digits)

    def get_bed_bath(self, item):
        raw = item.get("bed_and_bath")
        if not raw:
            return None, None

        text = self.__strip_html(raw)
        if not text:
            return None, None

        bed_match = re.search(r'(\d+)\s*BR', text, re.IGNORECASE)
        bath_match = re.search(r'(\d+)\s*Ba', text, re.IGNORECASE)

        bed = int(bed_match.group(1)) if bed_match else None
        bath = int(bath_match.group(1)) if bath_match else None

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

    def __strip_extra_spaces(self, text):
        text = text.replace("     ", ",").replace("   ", " ")
        return [part.strip() for part in text.split(",") if part.strip()]
        
    def __strip_spaces(self, text):
        return text.strip()
         
    def __strip_html(self,text):
        if not text:
            return None
        soup = BeautifulSoup(text, "html.parser")
        # get all text, strip whitespace, filter empty strings
        parts = [t.strip() for t in soup.get_text().split("\n") if t.strip()]
        return ", ".join(parts)

    def get_user_meta_tags(self, item):
        if item["user_meta_tags"] is None:
            return None

        text = self.__strip_html(item["user_meta_tags"])
        if not text:
            return None

        parts = self.__strip_extra_spaces(text)
        return ", ".join(parts) if isinstance(parts, list) else str(parts)


    def get_post_description(self, item):
        if item["post_description"] is None:
            return None

        text = self.__strip_html(item["post_description"])
        if not text:
            return None

        parts = self.__strip_extra_spaces(text)
        return " ".join(parts) if isinstance(parts, list) else str(parts)
    
