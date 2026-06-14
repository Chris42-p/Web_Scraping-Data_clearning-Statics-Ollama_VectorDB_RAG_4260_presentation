# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
from itemadapter import ItemAdapter


#==== Default imports 
# useful for handling different item types with a single interface
from itemadapter import ItemAdapter
from bs4 import BeautifulSoup
import ollama
from datetime import datetime
from typing import Optional
import json
import sys
import os

#=== internal lib import 
sys.path.append("/home/chris/Desktop/4260_presentation/Modules/spiders") #this is how to import std.obj

from .spider_interface import CONST

from spider_default_obj.spider_default_obj import Post_Data


class RealtorCaPipeline:
    def process_item(self, item, spider):
        print(item)
        return item
