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
     
     def clean_column_general_area(self):
          listings=self.__get_listings()



          #--case:   ' vancouver',' Vancouver' 
               #Capitalise & strip of white space  
          listings["general_area"]= listings["general_area"].str.strip() 
          listings["general_area"]= listings["general_area"].str.upper() 

          #-- case: 406XX W 14TH AVE VANCOUVER','34XXX W 19TH AVE VANCOUVER','38XXX W 35TH AVE VANCOUVER',
               #regex patterns: number (W) number(TH) (AVE) 
          re_pattern=(r"[\dX]+ W \d+TH AVE")




          # print(listings["general_area"].unique())
          # print(matched_df)

          #-----case :  '3 Beds 2 Baths Top Floor Suite Utilities Included',
          #-----case :  '3 Bedrooms 1.5 Bathrooms Middle Floor Suite Utilities Included',













     def control(self):

          self.clean_column_general_area()
          pass


Data_Cleaner().control()



