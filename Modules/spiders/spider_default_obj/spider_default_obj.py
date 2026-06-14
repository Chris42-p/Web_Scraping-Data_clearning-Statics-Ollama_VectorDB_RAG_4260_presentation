"""
Spider Standard Object

This is the default object all spiders should use to store listing data.
All spider objects should be mapped into this class before saving to the central DB.

Updated by: Yung (Philip)
- Fixed __init__ parameter list to match all self.xxx fields
- Added default values for optional fields
- Added to_dict() for DB/CSV storage
"""

import hashlib
from bs4 import BeautifulSoup
import ollama
from datetime import datetime
from typing import Optional
import json

#======= Custom libs 
from .spider_std_obj_interface import CONST


class Post_Data():
     
     time_scraped=None
     time_scraped_update =None
     post_active=None                   #Team IDK how to handle this RN please look over this

     def __init__(self, 
               post_id,time_of_post, user_post_title, first_pic, user_meta_tags, post_url, price_of_the_unit, sqr_feet, general_area, street_number, city, province, postal_code, bed_bath, square_feet_unit, post_description, rent_period, leasing_agent
          ):
   
          self.post_id=post_id
          self.time_of_post=time_of_post
          self.user_post_title=user_post_title
          self.first_pic=first_pic
          self.user_meta_tags=user_meta_tags
          self.post_url=post_url
          self.price_of_the_unit=price_of_the_unit
          self.sqr_feet=sqr_feet
          self.general_area=general_area
          self.street_number=street_number
          self.city=city
          self.province=province
          self.postal_code=postal_code
          self.bed_bath=bed_bath
          self.square_feet_unit=square_feet_unit
          self.post_description=post_description
          self.rent_period=rent_period
          self.leasing_agent=leasing_agent


          self.parse_description() #call parse description automatically. 
          self.get_current_time()

     def get_current_time(self):
          self.time_scraped= datetime.now().strftime("%Y-%m-%d %H:%M:%S")
          
     def set_time_scrated(self):
          self.time_scraped_update=datetime.now().strftime("%Y-%m-%d %H:%M:%S")

     def parse_description(self):
          if self.post_description != None:
               post_dec=self.Post_Description_Parser()
               post_dec.ingest_post_description(self.post_description)
               
     def save_to_db(self):
          print(self.post_id)
          print("=========Spider 'Saved' the content=======")
          #TODO
               #link this to the DB and make the object savable          
          pass

     class Post_Description_Parser:
          def __init__(self):
               # Basic Info
               self.smoke_free: Optional[bool] = None
               self.private_room: Optional[bool] = None
               self.living_situation: Optional[str] = None
               self.has_ac: Optional[bool] = None
               self.w_d_in_unit: Optional[bool] = None
               self.furnished: Optional[bool] = None
               self.wheelchair_accessible: Optional[bool] = None
               self.sq_footage: Optional[int] = None
               self.price_per_month: Optional[int] = None
               self.included_utilities: Optional[str] = None
               self.utility_cap: Optional[str] = None
               self.close_to: Optional[str] = None
               self.travel_convenience: Optional[str] = None
               self.luxuries: Optional[str] = None
               self.llm_model_comments: Optional[str] = None

               # Pet Policy
               self.pets_okay: Optional[bool] = None
               self.cats_okay: Optional[bool] = None
               self.dogs_okay: Optional[bool] = None

               # Parking
               self.parking_included: Optional[bool] = None
               self.parking_spots: Optional[int] = None
               self.parking_ev_charging: Optional[bool] = None
               self.parking_details: Optional[str] = None

               # Deposit
               self.damage_deposit: Optional[str] = None
               self.other_deposits: Optional[str] = None

               # Requirements
               self.req_credit_check: Optional[bool] = None
               self.req_references: Optional[bool] = None
               self.req_criminal_record_check: Optional[bool] = None
               self.req_other: Optional[str] = None

          def __parse_llm(self, response: str | dict):
               data = json.loads(response) if isinstance(response, str) else response

               # Basic Info
               self.smoke_free = data.get("smoke_free")
               self.private_room = data.get("private_room")
               self.living_situation = data.get("living_situation")
               self.living_situation = data.get("available_from")
               self.living_situation = data.get("property_type")
               self.has_ac = data.get("has_ac")
               self.w_d_in_unit = data.get("w_d_in_unit")
               self.furnished = data.get("furnished")
               self.wheelchair_accessible = data.get("wheelchair_accessible")
               self.sq_footage = data.get("sq_footage")
               self.price_per_month = data.get("price_per_month")
               self.included_utilities = data.get("included_utilities")
               self.utility_cap = data.get("utility_cap")
               self.close_to = data.get("close_to")
               self.travel_convenience = data.get("travel_convenience")
               self.luxuries = data.get("luxuries")
               self.llm_model_comments = data.get("llm_model_comments")

               # Pet Policy
               pets = data.get("pet_friendly", {})
               self.pets_okay = pets.get("pets_okay")
               self.cats_okay = pets.get("cats_okay")
               self.dogs_okay = pets.get("dogs_okay")

               # Parking
               parking = data.get("parking", {})
               self.parking_included = parking.get("included")
               self.parking_spots = parking.get("spots")
               self.parking_ev_charging = parking.get("ev_charging")
               self.parking_details = parking.get("details")

               # Deposit
               deposit = data.get("deposit", {})
               self.damage_deposit = deposit.get("damage_deposit")
               self.other_deposits = deposit.get("other_deposits")

               # Requirements
               req = data.get("requirements", {})
               self.req_credit_check = req.get("credit_check")
               self.req_references = req.get("references")
               self.req_criminal_record_check = req.get("criminal_record_check")
               self.req_other = req.get("other")
     
          def ingest_post_description(self, document):       #private method
               #ref: https://github.com/ollama/ollama-python
               crashes=0
               response=""
               while crashes<CONST["LLM_CRASH_LIMIT"]:
                    try:
                         print("\n====== Parsing Description Using LLM ===========\n") 
                         instruction= f"{CONST["LLM_OUTPUT_OBJ_INSTRUCTIONS"]} Document:{document}"
                         
                         response=ollama.chat(
                              model=CONST["MODEL_NAME"],          
                              messages=[
                                   {"role": "system","content": CONST["SYSTEM_ROLE"]},
                                   {"role": "user","content":instruction}],
                                   stream= True
                              )
                         full_response = ""
                         for chunk in response:
                              token = chunk['message']['content']
                              # print(token, end='', flush=True)
                              full_response += token

                         self.__parse_llm(full_response)
                         return full_response

                    except Exception as e:
                         crashes+=1
                         print(f"Ollama call:  {e}"  )
                         print("Model Crashed")               

               # return response #return empty string if the model keeps crashing.






# we can fall back on this one if needed. 
# class SpiderData_Default_Obj(): #clean input before putting into this obj
#     def __init__(self,
#         # Required fields
#         title,
#         listing_url,
#         source_website,
#         first_seen,
#         last_seen,
#         status,
#         address,
#         street_address,
#         neighbourhood,
#         city,
#         province,
#         price,
#         bedrooms,
#         bathrooms,
#         square_feet,
#         lot_size,
#         property_type,
#         features,
#         facilities,
#         agent_name,
#         brokerage,

#         # Optional fields (default N/A)
#         img_of_unit="N/A",
#         days_ago_posted="N/A",
#         post_updated="N/A",
#         post_description="N/A",
#         move_in_date="N/A",
#         security_deposit="N/A",
#         min_rental_period="N/A",
#         amenities="N/A",       # fixed typo: amenties → amenities
#         pet="N/A",
#         appliances="N/A",      # laundry, stove, dishwasher, washer, dryer
#         parking="N/A",
#         locker="N/A",
#         smoking="N/A",
#     ):
#         # == Meta: about the post
#         self.title = title
#         self.listing_url = listing_url
#         self.source_website = source_website
#         self.img_of_unit = img_of_unit

#         # == Market speed
#         self.days_ago_posted = days_ago_posted
#         self.post_updated = post_updated
#         self.first_seen = first_seen
#         self.last_seen = last_seen
#         self.status = status

#         # == Address of the home
#         self.address = address
#         self.street_address = street_address
#         self.neighbourhood = neighbourhood
#         self.city = city
#         self.province = province

#         # == About the unit
#         self.price = price
#         self.bedrooms = bedrooms
#         self.bathrooms = bathrooms
#         self.square_feet = square_feet
#         self.lot_size = lot_size
#         self.property_type = property_type
#         self.post_description = post_description
#         self.move_in_date = move_in_date
#         self.security_deposit = security_deposit
#         self.min_rental_period = min_rental_period

#         # == Features
#         self.amenities = amenities      # fixed typo: amenties → amenities
#         self.features = features
#         self.facilities = facilities
#         self.pet = pet
#         self.appliances = appliances    # laundry, stove, dishwasher, washer, dryer
#         self.parking = parking
#         self.locker = locker
#         self.smoking = smoking

#         # == Seller info
#         self.agent_name = agent_name
#         self.brokerage = brokerage

#     def get_hash(self) -> str:
#         """Generate unique hash from listing URL."""
#         return hashlib.md5(self.listing_url.encode()).hexdigest()

#     def to_dict(self) -> dict:
#         """Convert to dictionary for DB/CSV storage."""
#         return {
#             "listing_hash": self.get_hash(),
#             "title": self.title,
#             "listing_url": self.listing_url,
#             "source_website": self.source_website,
#             "img_of_unit": self.img_of_unit,
#             "days_ago_posted": self.days_ago_posted,
#             "post_updated": self.post_updated,
#             "first_seen": self.first_seen,
#             "last_seen": self.last_seen,
#             "status": self.status,
#             "address": self.address,
#             "street_address": self.street_address,
#             "neighbourhood": self.neighbourhood,
#             "city": self.city,
#             "province": self.province,
#             "price": self.price,
#             "bedrooms": self.bedrooms,
#             "bathrooms": self.bathrooms,
#             "square_feet": self.square_feet,
#             "lot_size": self.lot_size,
#             "property_type": self.property_type,
#             "post_description": self.post_description,
#             "move_in_date": self.move_in_date,
#             "security_deposit": self.security_deposit,
#             "min_rental_period": self.min_rental_period,
#             "amenities": self.amenities,
#             "features": self.features,
#             "facilities": self.facilities,
#             "pet": self.pet,
#             "appliances": self.appliances,
#             "parking": self.parking,
#             "locker": self.locker,
#             "smoking": self.smoking,
#             "agent_name": self.agent_name,
#             "brokerage": self.brokerage,
#         }
