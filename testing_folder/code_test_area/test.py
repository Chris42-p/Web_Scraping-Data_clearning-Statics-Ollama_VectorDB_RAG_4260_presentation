from bs4 import BeautifulSoup
import ollama
from datetime import datetime

class XX():
     content={'post_id': 'post id: 7938853846', 'time_of_post': '2026-06-04T16:24:38-0700', 'user_post_title': 'Richmond 3 BDRM House', 'first_pic': 'https://images.craigslist.org/00M0M_1H1TQh5hqcu_0CI0t2_600x450.jpg', 'user_meta_tags': '<div class="attrgroup">\n\n\n            <div class="attr pets_cat">\n                <span class="valu">              <a href="https://vancouver.craigslist.org/search/apa?pets_cat=1">cats are OK - purrr</a>\n</span>\n            </div>\n\n\n            <div class="attr">\n                <span class="valu">              <a href="https://vancouver.craigslist.org/search/apa?housing_type=6">house</a>\n</span>\n            </div>\n\n\n            <div class="attr pets_dog">\n                <span class="valu">              <a href="https://vancouver.craigslist.org/search/apa?pets_dog=1">dogs are OK - wooof</a>\n</span>\n            </div>\n\n\n            <div class="attr">\n                <span class="valu">              <a href="https://vancouver.craigslist.org/search/apa?laundry=1">w/d in unit</a>\n</span>\n            </div>\n\n\n            <div class="attr">\n                <span class="valu">              <a href="https://vancouver.craigslist.org/search/apa?parking=1">carport</a>\n</span>\n            </div>\n\n\n            <div class="attr no_smoking">\n                <span class="valu">              <a href="https://vancouver.craigslist.org/search/apa?no_smoking=1">no smoking</a>\n</span>\n            </div>\n    </div>', 'post_url': 'https://vancouver.craigslist.org/rch/apa/d/richmond-richmond-bdrm-house/7938853846.html', 'price_of_the_unit': '$2,850', 'num_bedrooms_n_square_feet_sq': '/ 3br - 2124ft', 'city_general_area': ' (Boyd Park)', 'address': None, 'bed_and_bath': '<span class="attr important">\n                3BR / 2Ba\n            </span>', 'square_feet_unit': '<span class="attr important">\n                2124ft<sup>2</sup>\n            </span>', 'post_description': '<section id="postingbody">\n        <div class="print-information print-qrcode-container">\n            <p class="print-qrcode-label">QR Code Link to This Post</p>\n            <div class="print-qrcode" data-location="https://vancouver.craigslist.org/rch/apa/d/richmond-richmond-bdrm-house/7938853846.html">\n            </div>\n        </div>\n3 bedroom 2 bathroom house for rent<br>\nLarge fenced backyard<br>\n<br>\nRM Grauer Elementary school and park one block away<br>\nHugh Boyd Secondary school catchement<br>\n<br>\nSpacious well-loved 3 bedroom house with ample storage space. Additional room can be added if needed.  House will be rented AS-IS.<br>\nSteps away from bus stations, grocery stores and restaurants.<br>\n<br>\nBedroom 3<br>\nBathrooms: 2<br>\n<br>\nParking : carport<br>\n<br>\nAvailable: July 1, 2026<br>\n<br>\nIdeal Tenants:<br>\nClean, Respectful, Quiet tenants, families, students<br>\nLease Term: 6 to 12 months  <br>\nDeposits: half a month\'s rent<br>\nTenant insurance required<br>\nAbsolutely no smoking, no vaping, no drugs, no sublets<br>\n<br>\nCredit/Reference/Employment Check: required<br>\n<br>\nIf interested please email and tell us about your situation.<br>\n- Full Name and Number of Occupants<br>\n- Background of Each Tenant<br>\n- Expected Move-In Date and Length of Lease Term<br>\n- Availability for viewings<br>\n<br>\nThanks for your time.<br>\n    </section>', 'rent_period': 'monthly'}

     llm_model_crash_limit=4

     def __init__(self,):
          self.__process_address(self.content["address"])

          # x=self.content["square_feet_unit"]
          # x=self.__strip_spaces(self.__strip_html(x))
          # print(x[:-1])

     def __process_address(self, text):
        # 'address': '815 SW Marine Dr, Vancouver, BC V6P5Y9', 
        text=text.split(",")
        street_number=text[0]
        city=text[1]
        province=text[2].split(" ")[0]
        postal_code=text[2].split(" ")[1]
        
        return street_number, city, province, postal_code


     def __strip_extra_spaces(self, text) :
        text=text.replace("     ",",").replace("   ","") #custom for cregslist prasing of data 
        return text.split(",")
        
     def __strip_spaces(self, text):
         return text.strip()
         
    
     def __strip_newline(self,text):
          return text.replace("\n","")
          
     
     def __strip_html(self,text):
        return BeautifulSoup(text, "html.parser").get_text()
        pass
     



from bs4 import BeautifulSoup
import ollama
from datetime import datetime

from typing import Optional
import json


# class Post_Data():
     
#      time_scraped=None
#      time_scraped_update =None
#      post_active=None                   #Team IDK how to handle this RN please look over this

#      def __init__(self, post_id, time_of_post, user_post_title, first_pic, user_meta_tags, post_url, price_of_the_unit, num_bedrooms_n_square_feet_sq, city_general_area, address, bed_and_bath, square_feet_unit, post_description, rent_period):
#           self.post_id=post_id

#           self.time_of_post=time_of_post
#           self.user_post_title=user_post_title
#           self.first_pic=first_pic
#           self.user_meta_tags=user_meta_tags
#           self.post_url=post_url
#           self.price_of_the_unit=price_of_the_unit
#           self.num_bedrooms_n_square_feet_sq=num_bedrooms_n_square_feet_sq
#           self.city_general_area=city_general_area
#           self.address=address
#           self.bed_and_bath=bed_and_bath
#           self.square_feet_unit=square_feet_unit
#           self.post_description=post_description
#           self.rent_period=rent_period

#           self.parse_description() #call parse description automatically. 
#           self.get_current_time()

#      def get_current_time(self):
#           self.time_scraped= datetime.now().strftime("%Y-%m-%d %H:%M:%S")
          
#      def set_time_scrated(self):
#           self.time_scraped_update=datetime.now().strftime("%Y-%m-%d %H:%M:%S")
     
     


#      def parse_description(self):
#           if self.post_description != None:
#                post_dec=self.Post_Description_Parser()
#                post_dec.ingest_post_description(self.post_description)
               
#           pass
     
#      class Post_Description_Parser:
     
#           def __init__(self):
#           # Basic Info
#           self.smoke_free: Optional[bool] = None
#           self.private_room: Optional[bool] = None
#           self.living_situation: Optional[str] = None
#           self.has_ac: Optional[bool] = None
#           self.w_d_in_unit: Optional[bool] = None
#           self.furnished: Optional[bool] = None
#           self.wheelchair_accessible: Optional[bool] = None
#           self.sq_footage: Optional[int] = None
#           self.price_per_month: Optional[int] = None
#           self.included_utilities: Optional[str] = None
#           self.utility_cap: Optional[str] = None
#           self.close_to: Optional[str] = None
#           self.travel_convenience: Optional[str] = None
#           self.luxuries: Optional[str] = None
#           self.llm_model_comments: Optional[str] = None

#           # Pet Policy
#           self.pets_okay: Optional[bool] = None
#           self.cats_okay: Optional[bool] = None
#           self.dogs_okay: Optional[bool] = None

#           # Parking
#           self.parking_included: Optional[bool] = None
#           self.parking_spots: Optional[int] = None
#           self.parking_ev_charging: Optional[bool] = None
#           self.parking_details: Optional[str] = None

#           # Deposit
#           self.damage_deposit: Optional[str] = None
#           self.other_deposits: Optional[str] = None

#           # Requirements
#           self.req_credit_check: Optional[bool] = None
#           self.req_references: Optional[bool] = None
#           self.req_criminal_record_check: Optional[bool] = None
#           self.req_other: Optional[str] = None

#           def __parse_llm(self, response: str | dict):
#                data = json.loads(response) if isinstance(response, str) else response

#                # Basic Info
#                self.smoke_free = data.get("smoke_free")
#                self.private_room = data.get("private_room")
#                self.living_situation = data.get("living_situation")
#                self.has_ac = data.get("has_ac")
#                self.w_d_in_unit = data.get("w_d_in_unit")
#                self.furnished = data.get("furnished")
#                self.wheelchair_accessible = data.get("wheelchair_accessible")
#                self.sq_footage = data.get("sq_footage")
#                self.price_per_month = data.get("price_per_month")
#                self.included_utilities = data.get("included_utilities")
#                self.utility_cap = data.get("utility_cap")
#                self.close_to = data.get("close_to")
#                self.travel_convenience = data.get("travel_convenience")
#                self.luxuries = data.get("luxuries")
#                self.llm_model_comments = data.get("llm_model_comments")

#                # Pet Policy
#                pets = data.get("pet_friendly", {})
#                self.pets_okay = pets.get("pets_okay")
#                self.cats_okay = pets.get("cats_okay")
#                self.dogs_okay = pets.get("dogs_okay")

#                # Parking
#                parking = data.get("parking", {})
#                self.parking_included = parking.get("included")
#                self.parking_spots = parking.get("spots")
#                self.parking_ev_charging = parking.get("ev_charging")
#                self.parking_details = parking.get("details")

#                # Deposit
#                deposit = data.get("deposit", {})
#                self.damage_deposit = deposit.get("damage_deposit")
#                self.other_deposits = deposit.get("other_deposits")

#                # Requirements
#                req = data.get("requirements", {})
#                self.req_credit_check = req.get("credit_check")
#                self.req_references = req.get("references")
#                self.req_criminal_record_check = req.get("criminal_record_check")
#                self.req_other = req.get("other")

     
#           def ingest_post_description(self, document):       #private method
#                #ref: https://github.com/ollama/ollama-python
#                crashes=0
#                response=""
#                while crashes<self.llm_model_crash_limit:
#                     # try:
#                          print("sending request to model ")
                         
#                          # content=f"{CONST['PROMPT']} \n {document}"
#                          response=ollama.chat(
#                               # model=CONST["MODEL_NAME"],               llama3.2:latest
#                               model="llama3.2:latest",               
#                               messages=[
#                               {
#                                    "role": "system",
#                                    "content": """
#                                    You are a precise data extraction engine.

#                                    DENEFITIONS:                              
#                                    - "own laundry" and "in-suite laundry" both mean w_d_in_unit: true
#                                    - Extract price if mentioned anywhere in the document
#                                    - "utilities included" should always populate included_utilities, never left null
#                                    - Explicit square footage should always populate sq_footage

#                                    BEHAVIOR:
#                                    - Return ONLY valid JSON, no preamble, no markdown, no code blocks
#                                    - Any observations go ONLY in "llm_model_comments"
#                                    - Write values as direct statements, not meta-commentary

#                                    HANDLING MISSING DATA:
#                                    - Set field to null if no relevant information is found
#                                    - Do not infer or assume information not in the document

#                                    OUTPUT FORMAT RULES:
#                                    - BAD:  "amenities": "This is a 30 word description of the living space."
#                                    - GOOD: "amenities": "Spacious open-concept kitchen with hardwood floors and in-suite laundry."

#                                    - BAD:  "close_to": "The document mentions the unit is close to a park."
#                                    - GOOD: "close_to": "Located one block from Central Park and near two grocery stores."
#                                    """
#                               },
#                               {
#                                    "role": "user",
#                                    "content": f"""
#      {{
#      "smoke_free": bool or null,
#      "pet_friendly": {{
#           "pets_okay": bool or null,
#           "cats_okay": bool or null,
#           "dogs_okay": bool or null
#      }},
#      "private_room": bool or null,
#      "living_situation": "50 word description of the living arrangement or null",
#      "available_from": "on which date does the unit become availale or null",
#      "has_ac": bool or null,
#      "w_d_in_unit": bool or null,
#      "furnished": bool or null,                     
#      "wheelchair_accessible": bool or null,         
#      "sq_footage": int or null,                     
#      "price_per_month": int or null,                
#      "parking": {{
#           "included": bool or null,
#           "spots": int or null,
#           "ev_charging": bool or null,               
#           "details": "location and cost details or null"
#      }},
#      "deposit": {{
#           "damage_deposit": "amount and conditions or null",
#           "other_deposits": "any additional deposits or null"
#      }},
#      "included_utilities": "list of included utilities (internet, water, heat, etc.) or null",
#      "utility_cap": "any conditions on utility inclusion (e.g. capped at X people) or null", # new
#      "requirements": {{
#           "credit_check": bool or null,
#           "references": bool or null,
#           "criminal_record_check": bool or null,
#           "other": "any other requirements or null"
#      }},
#      "close_to": "nearby attractions, parks, schools, grocery stores or null",
#      "travel_convenience": "proximity to transit (bus, skytrain) or null",
#      "luxuries": "100 word summary of premium features, pool, views, appliances, etc. or null",
#      "llm_model_comments": "observations, uncertainties, or missing info or null"
#      }}

#      Document:
#      {document}
#      """
# }
#      ],
#                                    stream= True
#                               )

#                          full_response = ""
#                          for chunk in response:
#                               token = chunk['message']['content']
#                               # print(token, end='', flush=True)
#                               full_response += token

#                          self.__parse_llm(full_response)
#                          return full_response

#                     # except Exception as e:
#                     #      crashes+=1
#                     #      # print(f"Ollama call:  {e}"  )
#                     #      print("Model Crashed")               

#                # return response #return empty string if the model keeps crashing.


XX()



