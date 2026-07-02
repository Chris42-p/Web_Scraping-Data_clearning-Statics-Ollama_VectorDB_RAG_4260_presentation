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
    
     def __init__(self):
          pass
    
     def __get_listings(self):
          post=Post_Data()
          listings= post.get_all_listings()
          return listings
     
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
     
     def clean_street_number(self, listings, display): #the data is fine ish
          col_pd="street_number"

          # listings[col_pd].fillna("0 abc road")








     # -- Engine: display -- goal is to minimize count (reduce uniques)
          if display:
               count=0
               print(f"\n\n")
               for x in (listings[col_pd].unique()):
                    print(f"{x}")
                    count+=1
               print(f"length: {count}")

          pass

     def clean_postal_code(self, listings, display):
          #TODO: look up the address with the geopy library fill what i can. 

          col_pd_postal="postal_code"
          col_pd_address="street_number"
          # listings[col_pd] 



          # geolocator = Nominatim(user_agent="postal_lookup")
          # for x in listings[col_pd_address]:
          #      # location = geolocator.geocode(listings[col_pd_address])
          #      print(x)
          
          print(listings[col_pd_address][0][1])


     # -- Engine: display -- goal is to minimize count (reduce uniques)
          if False:
               count=0
               print(f"\n\n")
               for x in (listings[col_pd_postal].unique()):
                    
                    print(f"{x}\t{listings[col_pd_address][count]  }")

                    count+=1
               print(f"length: {count}")

          pass


     def control(self):
          listings=self.__get_listings()
          
          self.clean_column_general_area(listings,False)
          self.clean_street_number(listings, False)
          self.clean_postal_code(listings, True)







Data_Cleaner().control()



