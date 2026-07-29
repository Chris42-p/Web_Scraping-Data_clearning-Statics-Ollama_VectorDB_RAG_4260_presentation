# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
from itemadapter import ItemAdapter
from .realtylink_interface import CONST
#=== Scrapy import 

from datetime import datetime 
import sys
import re 
#== reg imports

#== IMPORT THE DEFUALT OBJECT DYNAMICALLY =====
from pathlib import Path
import sys

from geopy.geocoders import Nominatim
import time

# walk up until we find the folder that contains 'Modules'
current = Path(__file__).resolve()
for parent in current.parents:
    if (parent / "Modules").exists():
        sys.path.append(str(parent))
        break

from Modules.spiders.spider_default_obj.spider_default_obj import Post_Data
#==========================

class RealtylinkPipeline:
    def process_item(self, item, spider):
        if CONST["SHOW_TEXT"]:
            print(f"\n\n====== PARSING THE CRAWLED OBJECT ======\n\n {item} \n\n")

        street_number, general_area, city, province, postal_code = self._process_address(item.get("unit_address"))

        latitude, longitude, address_osm = self._geocode_address(
            street_number,
            city,
            province,
            postal_code,
        )
        time.sleep(1)

        post = Post_Data(
            post_id=self.get_post_id(item),
            time_of_post=self.time_of_post(item),
            user_post_title=self.user_post_title(item),
            user_meta_tags=self.user_meta_tags(item),
            post_url=self.post_url(item),
            price_of_the_unit=self.price_of_the_unit(item),
            sqr_feet=self.sqr_feet_lot(item),
            general_area=general_area,
            street_number=street_number,
            city=city,
            province=province,
            postal_code=postal_code,
            latitude=latitude,
            longitude=longitude,
            address_osm=address_osm,
            bed=self.get_bed(item),
            bath=self.get_bath(item),
            square_feet_unit=self.square_feet_unit(item),
            post_description=self.post_description(item),
            rent_period=self.rent_period(item),
            leasing_agent=self.leasing_agent(item),
            source_spider=spider.name,
            first_pic=self.first_img_url(item),
            img_url=self.first_img_url(item),
        )

        post.save_new_post_to_db()

        item["latitude"] = latitude
        item["longitude"] = longitude
        item["address_osm"] = address_osm

        return item

    def _geocode_address(self, street_number, city, province, postal_code):
        parts = [street_number, city, province, postal_code, "Canada"]
        query = ", ".join([part for part in parts if part and part != "N/A"])

        try:
            geolocator = Nominatim(user_agent="housing_scraper_geocoder")
            location = geolocator.geocode(query, timeout=10)
            if not location:
                return None, None, None

            return float(location.latitude), float(location.longitude), location.address
        except Exception as exc:
            print(f"Geocode failed for '{query}': {exc}")
            return None, None, None

    def _process_address(self, unit_address):
        if not unit_address:
            return None, None, "Vancouver", "BC", None

        cleaned = re.sub(r"\s+", " ", unit_address).strip()
        parts = [p.strip() for p in cleaned.split(",") if p.strip()]

        street_number = parts[0] if len(parts) > 0 else None
        general_area = parts[1] if len(parts) > 1 else None
        city = parts[2] if len(parts) > 2 else "Vancouver"
        province = "BC"
        postal_code = None

        return street_number, general_area, city, province, postal_code
    
    def sqr_feet_lot(self,item):
        return "RealtyLink dose not provide this"

    def first_img_url(self,item):
        if item["first_pic"] ==None:
            return None
        
        return item["first_pic"]

    def get_post_id(self, item):
        if item["url"] ==None:
            return None
        
        return item["url"].split("/")[-1]

    def time_of_post(self, item):
        return datetime.now().strftime("%Y-%m-%d %H:%M:%S")  # '2026-06-13 12:30:45'
    
    def user_post_title(self, item):
        if item["unit_type"] ==None:
            return None
        
        return item["unit_type"].split(" ")[0]


    def user_meta_tags(self, item):
        if item["property_metadata"] ==None:
            return None
        
        return (str(item["property_metadata"]))

    def post_url(self, item):
        if item["url"] ==None:
            return None
        
        return item["url"]

    def price_of_the_unit(self, item):
        if item.get("unit_price") is None:
            return None

        return item["unit_price"]

    def sqr_feet(self, item):
        #this is for lot size -- this website dosent provide lot size 
        return None #"None provided"

    def general_area(self, item):
        if item["unit_address"] ==None:
            return None
        
        x=item["unit_address"].replace("\n","").strip()
        return x.split(",")[1]

    def street_number(self, item):
        if item["unit_address"] ==None:
            return None
        
        x=item["unit_address"].replace("\n","").strip()
        return x.split(",")[0]
    
    def city(self, item):
        if item["unit_address"] ==None:
            return None
        
        x=item["unit_address"].replace("\n","").strip()
        return  x.split(",")[2]
    
    def province(self, item):
        return None#"Not available on realtylink"

    def postal_code(self, item):
        return None

    def get_bed(self, item):
        bed=0
        if item["bed"] ==None :
            bed=0
        else:
            bed= re.search(r'\d+',item["bed"]).group()

        return int(bed)
        
    def get_bath(self, item):
        bath = 0
        if item.get("bath") is None:
            bath = 0
        else:
            match = re.search(r'\d+', item["bath"])
            bath = match.group() if match else 0

        return int(bath)
    
    def square_feet_unit(self, item):
        if item["sqr_feet"] ==None:
            return None
        
        return item["sqr_feet"].replace("\n","").replace("sqft","").replace(",","").strip()
        
    def post_description(self, item):
        if item["description"] ==None:
            return None
        
        return item["description"].replace("\n","").strip()
    
    def rent_period(self, item):
        return None#"Not available on realtylink"

    def leasing_agent(self, item):
        if item["broker_agency"] ==None:
            return None
        
        return item["broker_agency"].replace("\n","").strip()


# ##=== Sample response 
# 2026-06-25 11:03:00 [scrapy.core.scraper] DEBUG: Scraped from <200 https://realtylink.org/en/house~for-rent~vancouver/263156536>
# {'url': 'https://realtylink.org/en/house~for-rent~vancouver/263156536', 'unit_address': '\n                                                1886 E 52ave Vancouver, Killarney VE, Vancouver\n                                            ', 'unit_price': '2000', 'sqr_feet': '\n                670 sqft\n            ', 'description': '\n                                                Bright and functional 2-bedroom, 1-bathroom suite offering approximately 670 sq.ft. of living space. Features a spacious living room, private entrance, and convenient location close to transit, schools, shopping, and daily amenities.  Rental Terms $2,000/month Utilities Included No Pets No Smoking, Vaping, or Drugs Tenant Insurance Required  Please provide: Full Name, Occupation, Number of Occupants, Desired Move-in Date, Lease Term, and a Brief Introduction.  Only Complete Inquiries Containing All Requested Information Will Receive a Response.\n                                            ', 'msl_numer': 'R3134909', 'bed': '2 bedrooms', 'bath': '1 bathroom', 'first_pic': 'https://media.realtylink.org/images/consumersite/property/263156536/aece905e67134d24b3c1541444def103.jpeg?width=640&height=480&fit=cover', 'property_metadata': {'Floor Area': '\n                670 sqft\n            ', 'Interior Features': None, 'Laundry Features': None, 'Appliances': None, 'Exterior Features': None, 'Parking Spaces': None, 'Amenities': None, 'Cooling Features': None, 'Bylaws Restriction': None}}