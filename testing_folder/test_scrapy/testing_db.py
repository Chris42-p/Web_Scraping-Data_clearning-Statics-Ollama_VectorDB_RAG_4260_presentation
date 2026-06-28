
import sqlite3
from pathlib import Path
import hashlib
from bs4 import BeautifulSoup
import ollama
from datetime import datetime
from typing import Optional
import json


CONST={
     #=== DB Name and location
     "DB_LOCATION":"spider_central_db",
     "DB_NAME":"spider_central.DB",
 
     "":"",
     "":"",
     "":"",
     "":"",
     "":"",
     "":"",

}

def save_to_db(self):
     base=Path(__file__).resolve().parent
     db_path =f"{base}/{CONST["DB_LOCATION"]}/{CONST["DB_NAME"]}" 

     conn = sqlite3.connect(db_path)
     cursor = conn.cursor()

     cursor.execute("""
          INSERT OR REPLACE INTO posts (
               
               post_id,
               source_website,
               post_url,
               time_of_post,
               time_scraped,
               time_scraped_update,
               post_active
          )
          VALUES (?, ?, ?, ?, ?, ?, ?)
     """, (
          self.post_id,
          "N/A",
          self.post_url,
          self.time_of_post,
          self.time_scraped,
          self.time_scraped_update,
          1
     ))

     cursor.execute("""
          INSERT OR REPLACE INTO listings (
               post_id,
               user_post_title,
               price_of_the_unit,
               rent_period,
               city_general_area,
               address
          )
          VALUES (?, ?, ?, ?, ?, ?)
     """, (
          self.post_id,
          self.user_post_title,
          self.price_of_the_unit,
          self.rent_period,
          self.general_area,
          self.street_number
     ))

     cursor.execute("""
          INSERT OR REPLACE INTO unit_details (
               post_id,
               bed_and_bath,
               square_feet_unit,
               num_bedrooms_n_square_feet,
               first_pic,
               user_meta_tags
          )
          VALUES (?, ?, ?, ?, ?, ?)
     """, (
          self.post_id,
          self.bed_bath,
          self.square_feet_unit,
          self.sqr_feet,
          self.first_pic,
          str(self.user_meta_tags)
     ))

     cursor.execute("""
     INSERT OR REPLACE INTO parsed_description (
          smoke_free,
          private_room,
          living_situation,
          has_ac,
          w_d_in_unit,
          furnished,
          wheelchair_accessible,
          sq_footage,
          price_per_month,
          included_utilities,
          utility_cap,
          close_to,
          travel_convenience,
          luxuries,
          llm_model_comments,
          pets_okay,
          cats_okay,
          dogs_okay,
          parking_included,
          parking_spots,
          parking_ev_charging,
          parking_details,
          damage_deposit,
          other_deposits,
          req_credit_check,
          req_references,
          req_criminal_record_check,
          req_other
     )
     VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""", (
     self.post_description_obj.smoke_free,
     self.post_description_obj.private_room,
     self.post_description_obj.living_situation,
     self.post_description_obj.has_ac,
     self.post_description_obj.w_d_in_unit,
     self.post_description_obj.furnished,
     self.post_description_obj.wheelchair_accessible,
     self.post_description_obj.sq_footage,
     self.post_description_obj.price_per_month,
     self.post_description_obj.included_utilities,
     self.post_description_obj.utility_cap,
     self.post_description_obj.close_to,
     self.post_description_obj.travel_convenience,
     self.post_description_obj.luxuries,
     self.post_description_obj.llm_model_comments,
     self.post_description_obj.pets_okay,
     self.post_description_obj.cats_okay,
     self.post_description_obj.dogs_okay,
     self.post_description_obj.parking_included,
     self.post_description_obj.parking_spots,
     self.post_description_obj.parking_ev_charging,
     self.post_description_obj.parking_details,
     self.post_description_obj.damage_deposit,
     self.post_description_obj.other_deposits,
     self.post_description_obj.req_credit_check,
     self.post_description_obj.req_references,
     self.post_description_obj.req_criminal_record_check,
     self.post_description_obj.req_other,
     ))
     

     conn.commit()
     conn.close()

     print(self.post_id)
     print("=========Spider saved the content to central DB=======")
