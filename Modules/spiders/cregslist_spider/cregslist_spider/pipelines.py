# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html




#=== internal lib import 
from .spider_interface import CONST
from ...spider_default_obj import SpiderData_Default_Obj 


#==== Default imports 
# useful for handling different item types with a single interface
from itemadapter import ItemAdapter



class CregslistSpiderPipeline:
    def process_item(self, item, spider):
        #--        
        

        return item
  
    def __drop_html_tags():
        pass

    def __process_into_def_obj_n_save():
        SpiderData_Default_Obj(

        )
        pass


#==== ref obj

# yield{ #pass this obj into pipeline .
# #=== meta 
# # -- post ID/PK :
# "post_id": response.css("div.postinginfos >p.postinginfo::text").get(),

# # time of the post: 
# "time_of_post ":response.css("section.body div.reply-button-row p.postinginfo.reveal time::attr(datetime)").get(),
# "user_post_title":response.css("h1.postingtitle  span#titletextonly::text").get(),
# "first_pic":response.css("img::attr(src)").get(),
# "user_meta_tags":response.css("div.attrgroup:nth-child(4) ").get(), # nested attributed, need to process in.py
# "post_url":response.url,

# #== home  
# "price_of_the_unit": response.css("h1.postingtitle  span.price::text").get(),
# "num_bedrooms_n_square_feet_sq": response.css("h1.postingtitle  span.housing::text").get(), #--- process this to, isolate each value
# "city_general_area": response.css("h1.postingtitle .postingtitletext span:last-child::text").get(),
# "address":response.css("h2.street-address::text").get(),                                                #---- process me 
# "bed_and_bath": response.css("div.mapAndAttrs >div.attrgroup span.attr.important:nth-child(1)").get(),  #--- process me 
# "square_feet_unit":response.css("div.mapAndAttrs >div.attrgroup span.attr.important:nth-child(2)").get(),

# #== Amenetirs and living conditions -- LLM process
# "post_description":response.css("section#postingbody").get(),   #---------- make LLM to process this content down. 
# "rent_period": response.css("span.valu > a::text").get(),    
# }