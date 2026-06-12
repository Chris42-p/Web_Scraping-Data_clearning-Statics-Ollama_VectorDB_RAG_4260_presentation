from bs4 import BeautifulSoup
import ollama
from datetime import datetime

class XX():
     content={'post_id': 'post id: 7933065454', 
              'time_of_post': '2026-05-08T14:52:55-0700', 
              'user_post_title': 'Garden level suite with spectacular view, 2 bed, 2 bath.', 
              'first_pic': 'https://images.craigslist.org/00202_aMWkT5dcbzW_0CI0t2_600x450.jpg', 
              
              'user_meta_tags': '<div class="attrgroup">\n\n\n            <div class="attr">\n                <span class="valu">              <a href="https://vancouver.craigslist.org/search/apa?housing_type=6">house</a>\n</span>\n            </div>\n\n\n            <div class="attr">\n                <span class="valu">              <a href="https://vancouver.craigslist.org/search/apa?laundry=1">w/d in unit</a>\n</span>\n            </div>\n\n\n            <div class="attr">\n                <span class="valu">              <a href="https://vancouver.craigslist.org/search/apa?parking=5">street parking</a>\n</span>\n            </div>\n\n\n            <div class="attr no_smoking">\n                <span class="valu">              <a href="https://vancouver.craigslist.org/search/apa?no_smoking=1">no smoking</a>\n</span>\n            </div>\n    </div>',
               'post_url': 'https://vancouver.craigslist.org/nvn/apa/d/west-vancouver-garden-level-suite-with/7933065454.html', 
               'address': '815 SW Marine Dr, Vancouver, BC V6P5Y9', 
               'city_general_area': ' (West Vancouver)', 
               
               'price_of_the_unit': '$4,000', 
               'num_bedrooms_n_square_feet_sq': '/ 2br - 1500ft', 
               'square_feet_unit': '<span class="attr important">\n                1500ft<sup>2</up>\n            </span>', 
               'bed_and_bath': '<span class="attr important">\n                2BR / 2Ba\n            </span>', 

               'post_description': '<section id="postingbody">\n        <div class="print-information print-qrcode-container">\n            <p class="print-qrcode-label">QR Code Link to This Post</p>\n            <div class="print-qrcode" data-location="https://vancouver.craigslist.org/nvn/apa/d/west-vancouver-garden-level-suite-with/7933065454.html">\n            </div>\n        </div>\nSpectacular views of downtown Vancouver and Lions Gate from all rooms, located in a prime West Van neighborhood within the Chartwell Elementary and Sentinel Secondary school catchments. This 1,500 sqf garden level suite features high ceiling (9 feet), layout includes 2 large bedrooms, all with bathroom inside (ensuite). All bedrooms and living room have full glass doors from floor to ceiling, opening up to a flat backyard with a swimming pool and spectacular views. Complete privacy with own entrance and own laundry. Parking space for 1 car in the front yard (not in the garage) and additional street parking. Price: $4,000/month, utilities and internet are already included. Available now.<br>\n**No smoking inside. **No pets. **Unfurnished. **Will require references and credit (income) check. **Not accessible by wheelchair. **Utilities are included for up to 4 people, and EV charging is NOT included. **Please email/text for questions or viewing.<br>\n    </section>', 
               'rent_period': 'monthly'
          }

     llm_model_crash_limit=4

     def __init__(self,):
          x=self.content["square_feet_unit"]
          x=self.__strip_spaces(self.__strip_html(x))
          print(x[:-1])


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



