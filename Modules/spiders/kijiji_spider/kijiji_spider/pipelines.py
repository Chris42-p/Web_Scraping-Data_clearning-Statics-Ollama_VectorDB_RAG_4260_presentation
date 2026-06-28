"""
Kijiji Spider Pipeline

Follows cregslist_spider pipeline pattern:
- Cleans raw scraped fields
- Maps into Post_Data from spider_default_obj
- Post_Data handles LLM parsing of post_description automatically

Post_Data parameter order (as of latest spider_default_obj.py):
    post_id, time_of_post, user_post_title, first_pic, user_meta_tags,
    post_url, price_of_the_unit, sqr_feet, general_area,
    street_number, city, province, postal_code,
    bed_bath, square_feet_unit, post_description, rent_period
"""

import re

from kijiji_spider.spider_interface import CONST

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


class KijijiSpiderPipeline:

    def process_item(self, item, spider):

        # == post_id
        post_id = str(item.get("post_id", "N/A")).strip()

        # == time_of_post
        time_of_post = item.get("time_of_post", "N/A")

        # == user_post_title
        user_post_title = item.get("user_post_title", "N/A")

        # == first_pic
        first_pic = item.get("first_pic", "N/A")

        # == user_meta_tags
        user_meta_tags = item.get("user_meta_tags", "N/A")

        # == post_url
        post_url = item.get("post_url", "N/A")

        # == price — strip to number only
        price_raw = str(item.get("price_of_the_unit", "N/A"))
        price_of_the_unit = re.sub(r"[^\d.]", "", price_raw) or "N/A"

        # == sqr_feet — from num_bedrooms_n_square_feet_sq
        sqr_feet = str(item.get("num_bedrooms_n_square_feet_sq", "N/A"))
        if sqr_feet == "0":
            sqr_feet = "Studio/Bachelor"

        # == general_area — city level
        general_area = self.__extract_city(item.get("city_general_area", "N/A"))

        # == address parsing — split into components
        address_raw = item.get("address", "N/A")
        street_number, city, province, postal_code = self.__process_address(address_raw)

        # == bed_bath
        bed,bath = self.__get_bed_bath(item)

        # == square_feet_unit
        sqft_raw = str(item.get("square_feet_unit", "N/A"))
        square_feet_unit = re.sub(r"[^\d]", "", sqft_raw) or "N/A"

        # == post_description
        post_description = item.get("post_description", "N/A")

        # == rent_period
        rent_period = item.get("rent_period", "monthly")

        # == Log for now
        # # spider.logger.info(
        # #     f"Item scraped: {post_id} | {user_post_title} | ${price_of_the_unit} | {address_raw} | lat={item.get('latitude')} lon={item.get('longitude')}"
        # )
        
        Post_Data(
            post_id=post_id, 
            post_url=post_url, 
            time_of_post=time_of_post, 
            leasing_agent=None, #leasing_agent, <--- Yung please add this when you can.  
            general_area=general_area, 
            street_number=street_number, 
            city=city, 
            province=province, 
            postal_code=postal_code, 
            price_of_the_unit=price_of_the_unit, 
            square_feet_unit=square_feet_unit, 
            bed=bed, 
            bath=bath, 
            rent_period=rent_period, 
            user_post_title=user_post_title, 
            first_img_url=first_pic, 
            user_meta_tags=user_meta_tags, 
            post_description=post_description,  #<-- tmp mute for dev
            sqr_feet_lot=None #<--- see if you can find this 

        ).save_new_post_to_db()

        # TODO: uncomment once spider_default_obj import issue is resolved
        # import sys, os
        # sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'spider_default_obj'))
        # from spider_default_obj import Post_Data
        # Post_Data(
        #     post_id, time_of_post, user_post_title, first_pic, user_meta_tags,
        #     post_url, price_of_the_unit, sqr_feet, general_area,
        #     street_number, city, province, postal_code,
        #     bed_bath, square_feet_unit, post_description, rent_period,
        # ).save_to_db()


    def __get_bed_bath(self,item):
        if item["bed_and_bath"]== None:
            return None
        
        x=item["bed_and_bath"].split("/")
        bed=re.search(r'\d+',x[0]).group()
        bath=re.search(r'\d+',x[1]).group()

        return bed, bath

    def __process_address(self, address: str):
        if not address or address == "N/A":
            return "N/A", "N/A", "N/A", "N/A"
        try:
            parts = address.split(",")
            street_number = parts[0].strip() if len(parts) > 0 else "N/A"
            city = parts[1].strip() if len(parts) > 1 else "N/A"
            province_postal = parts[2].strip() if len(parts) > 2 else ""
            province_parts = province_postal.split(" ")
            province = province_parts[0] if province_parts else "N/A"
            postal_code = " ".join(province_parts[1:]) if len(province_parts) > 1 else "N/A"
            return street_number, city, province, postal_code
        except Exception:
            return address, "N/A", "N/A", "N/A"

    def __extract_city(self, address: str) -> str:
        cities = [
            "North Vancouver", "West Vancouver", "Burnaby", "Richmond",
            "Surrey", "Coquitlam", "Port Coquitlam", "Port Moody",
            "New Westminster", "White Rock", "Langley", "Abbotsford",
            "Delta", "Maple Ridge",
        ]
        for city in cities:
            if city.lower() in str(address).lower():
                return city
        return "Vancouver"
