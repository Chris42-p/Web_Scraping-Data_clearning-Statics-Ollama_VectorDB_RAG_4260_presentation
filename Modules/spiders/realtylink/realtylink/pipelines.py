# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
from itemadapter import ItemAdapter
#=== Scrapy import 

import sys
#== reg imports

#== custom imports
sys.path.append("/home/chris/Desktop/4260_presentation/Modules/spiders") #this is how to import std.obj


from spider_default_obj.spider_default_obj import Post_Data



class RealtylinkPipeline:
    def process_item(self, item, spider):
        print(item)
        return item
