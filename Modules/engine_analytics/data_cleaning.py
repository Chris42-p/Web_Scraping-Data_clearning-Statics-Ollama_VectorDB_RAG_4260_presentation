# This file is going to be used to clean the data. 

# read the data from the database. 
# remove the Nulls - cover them up with 0's -- keep it consistent. 
# normalize the "general_area" -- some need regex others, others need to be stripped again
# need a address to postal code look up table. 


#-- visualization 
# claude prompt at the end :
# using matplotlib can i pull up a map of vancouver, add a layer for addresses, add a layer for postal codes?

#-- Saving process data into another table in the same DB 
#-- will need a SQL query that hits on foreign keys and selectes the items that're not processed -- figure out at the end. 


# libraries import
from pathlib import Path
import sys

import pandas as pd
import numpy as np
import importlib
from geopy.geocoders import Nominatim
from time import sleep

import os 
import re 

# walk up until we find the folder that contains 'Modules'
current = Path(__file__).resolve()
for parent in current.parents:
    if (parent / "Modules").exists():
        sys.path.append(str(parent))
        break

from Modules.spiders.spider_default_obj.spider_default_obj import Post_Data
#==========================


#==== Get all the data into a dataframe. 
class Data_Cleaner():
     TMP_DIR_PATH="tmp_csv"
     TMP_NAME_PATH="mid_processing_csv.csv"
     TMP_FILE_PATH=f"{TMP_DIR_PATH}/{TMP_NAME_PATH}"


     def __init__(self):
          pass
    
     def __get_listings(self):
          post=Post_Data()
          listings= post.get_all_listings()
          return listings

     def __tmp_save_to_csv(self, ):
          #create the file if it does not exist. 
          base_path=current.parent
          tmp_file_path=f"{base_path}/{self.TMP_DIR_PATH}"
          
          os.makedirs(tmp_file_path, exist_ok=True)
          return tmp_file_path
               

     def clean_column_general_area(self,listings, display=False): #TODO: minimize count: rn 89/ 

     #--case:   ' vancouver',' Vancouver' 
               #Capitalise & strip of white space  
          listings["general_area"]= listings["general_area"].str.strip() 
          listings["general_area"]= listings["general_area"].str.upper() 

     #-- case: NAN 
          listings["general_area"]= listings["general_area"].fillna("VANCOUVER")

     #-- case: S W
          re_pattern5=r"S\s+W\s+MARINE"
          listings["general_area"] = listings["general_area"].replace(re_pattern5,"MARINE", regex=True)

     #--: UBC, Vancouver UBC, UBC Campus. 
          re_pattern6=r".*UBC.*"
          listings["general_area"] = listings["general_area"].replace(re_pattern6,"UBC", regex=True)


     #-- case: OAKRIDGE VW,VICTORIA VE,KILLARNEY VE
               #remove the VE/VW
          re_pattern1=(r" V[EW]|W[V]") #vatch V [E or W]
          listings["general_area"]=listings["general_area"].str.replace(re_pattern1,"", regex=True)

     #-- case: DOWNTOWN VANCOUVER GRANVILLE AND DUNSMUIR, DOWNTOWN COAL HARBOUR, DOWNTOWN VANCOUVER, VANCOUVER DOWNTOWN
          re_pattern7 = r".*(?:VANCOUVER DOWNTOWN|DOWNTOWN VANCOUVER).*"
          listings["general_area"]=listings["general_area"].str.replace(re_pattern7,"DOWNTOWN", regex=True)





     #-- case: HASTINGS-SUNRISE)
               #remove -special characters
          re_pattern2=(r"[)-/–+|✨]") #match [ - or / or.. ]
          listings["general_area"]=listings["general_area"].str.replace(re_pattern2," ", regex=True)

     #-- case: SUITE AVAIL NOW, 1 BEDROOM   DEN


     # -- Case: VANCOUVER WEST DUNBAR AREA,VANCOUVER WEST, VANCOUVER WEST OAK ST,VANCOUVER WEST
          # re_pattern4= r"(VANCOUVER (WEST|EAST|SOUTH))"
          re_pattern4 = r"\b(VANCOUVER\s+(?:[^,\n]*?\s+)?(?:WEST|EAST|SOUTH))\b"
          matched=listings["general_area"].str.extractall(re_pattern4)

          for matched_index in range(len(matched)):
               index_in_matched_pd=matched.index.get_level_values(0)[matched_index]
               listings.loc[index_in_matched_pd,"general_area"]= matched.loc[index_in_matched_pd][0][0]
     
     # #-- case: BRAND NEW 1 BEDROOM  FLEX  BOUTIQUE CONCRETE HOME AT OKU,COZY 2 BED2BATH1 FLEX PENTHOUSE UNIT AT RIVER DISTRICT, PET FRIENDLY ONE BEDROOM APARTMENT IN MOUNT PLEASANT,
          re_pattern3 = r"\b(?:AT|IN|OF)\b\s+(\S+(?:\s+\S+)?)" #the regex pattern that matches the stirngs

          # Get the matching data 
          matched=listings["general_area"].str.extractall(re_pattern3) #get the rows that match pattern --30 min find

          #replace the values in the OG dataframe
          for index_of_str_matched in range(len(matched.index.get_level_values(0))):
               index_in_matched_pd=matched.index.get_level_values(0)[index_of_str_matched]
               listings.loc[index_in_matched_pd,"general_area"]= matched.loc[index_in_matched_pd][0][0]
     


     # -- Engine: display -- goal is to minimize count (reduce uniques)
          if display:
               count=0
               print(f"\n\n")
               for x in (listings["general_area"].unique()):
                    print(f"{x}")
                    count+=1
               print(f"length: {count}")
          


          return listings
     
     def clean_street_number(self, listings, display):  #  492 #the data is fine ish
          col_pd="street_number"

          #=== case: 1 bed suite 3900 w 24th avenue, suite-779 shaw avenue
          regex_1 = r"^.*?suite[-\s\d]*\s"
          listings[col_pd]=listings[col_pd].str.replace(regex_1,"", case=False, regex=True)

          #== case 2: 1/2 basement 1115 w 48th avenue, bsmt 8290 montcalm street, BSMT 8290 Montcalm Street : 487
          regex_2 = r"^.*?(basement|bsmt)\s"
          listings[col_pd]=listings[col_pd].str.replace(regex_2,"", case=False, regex=True)

          #== case 3: 5xxx cartier st,3xx8 w 44 avenue, x10 388 kootenay street, xx1 198 aquarius mews
          regex_3 = r"x{1,3}\d*\s"
          listings[col_pd]=listings[col_pd].str.replace(regex_3," ", case=False, regex=True)

          #== case 4: nan
          listings[col_pd]=listings[col_pd].fillna("vancouver")
          
          #== case 5: HORNBY STREET
          listings[col_pd]=listings[col_pd].str.lower()

          #==case 6: w.48th av
          listings[col_pd]=listings[col_pd].str.replace(".", " ")
          
          #==case 7: #2 2596 oak street
          listings[col_pd]=listings[col_pd].str.replace("#", "")

          #== case 8: main and above 1chartwell drive




     # -- Engine: display -- goal is to minimize count (reduce uniques)
          if display:
               count=0
               print(f"\n\n")
               for x in (listings[col_pd].unique()):
                    print(f"{x}")
                    count+=1
               print(f"length: {count}")

          pass

     def clean_postal_code(self, listings, tmp_write_location, display):
          #TODO: look up the address with the geopy library fill what i can. 
               #-- going to save every 10 entries to a tmp file. 

          address_list="street_number"
          postal_code="postal_code"
     
          #try and find the postal codes for the address
          for index in range(len(listings[address_list])):
               #its DB entries they will be the same length. 
               address_=str(listings[address_list].loc[index])
               postal_=listings[postal_code].loc[index]

               #clean the entry. 
               postal_ind=str(postal_).strip().lower()
               
               if postal_ind =="n/a" or postal_ind =="nan": 
                    if address_ == "vancouver": #NA/nan is replaced with Vancouver in previous step 
                         
                         #static vlaue to ingest for row.  
                         bounding_box=['49.1989306', '49.3161714', '-123.2249611', '-123.0232419'] #from api 
                         display_name='Vancouver, Metro Vancouver Regional District, British Columbia, Canada'
                         #capture API reply info. 
                         listings.loc[index , "boundingbox"] =str(bounding_box)
                         listings.loc[index , "building_type"] = None
                         listings.loc[index, "address_osm"] =display_name
                         listings.loc[index , postal_code] = None
                         continue

                    try:
                         #send API request
                         geolocator = Nominatim(user_agent="test_test_test")
                         location = geolocator.geocode(address_)
                         
                         #if the api fails - skip the none values
                         if location == None:
                              continue

                         #TODO: check if the returned address is 
                         regex_city=r"vancouver"
                         van_only=re.search(regex_city, location.raw["display_name"], re.IGNORECASE)
                         if van_only ==None:
                              continue 

                         print(van_only)


                         #get the postal code from the reply 
                         regex_postal = r"[A-Z]\d[A-Z]\s?\d[A-Z]\d"
                         postal_code_found=re.search(regex_postal, location.raw["display_name"])[0]

                         #capture API reply info. 
                         listings.loc[index, "boundingbox"] =str(location.raw["boundingbox"])
                         listings.loc[index, "building_type"] = location.raw["type"]
                         listings.loc[index, "address_osm"] =location.raw["display_name"]
                         listings.loc[index, postal_code] = postal_code_found

                    except Exception as e:
                         print(f"Error: cleaning postal code: API request: {e}")
                         print(f"{location}\n\n")

                    if index %10: #going to over write the file 
                         listings.to_csv(f"{tmp_write_location}/{self.TMP_NAME_PATH}",index=False, header=True, mode="w")

                    sleep(.5) #need to slow down API else it'll rate limit me. 

          #merge the data frames 

     # -- Engine: display -- goal is to minimize count (reduce uniques)
          if False: 
               count=0
               print(f"\n\n")
               for x in (listings[col_pd_postal].unique()):
                    
                    print(f"{x}\t{listings[col_pd_address][count]  }")

                    count+=1
               print(f"length: {count}")


     def __convert_csv_to_pd_df(self,tmp_write_location ):
          #TODO: sent this new cleaned object into a table called "cleaned data"
          pass

     def __delete_temp_csv_file(self):
          #TODO: delete the csv tmp_csv and the file.  

          pass

     def control(self):
          #== supporters 
          listings=self.__get_listings()
          tmp_write_location=self.__tmp_save_to_csv()

          #== data processing. 
          self.clean_column_general_area(listings,False)
          self.clean_street_number(listings, False)
          self.clean_postal_code(listings,tmp_write_location, True)
          
          self.__convert_csv_to_pd_df(tmp_write_location, )
          self.__delete_temp_csv_file(tmp_write_location)





Data_Cleaner().control()



