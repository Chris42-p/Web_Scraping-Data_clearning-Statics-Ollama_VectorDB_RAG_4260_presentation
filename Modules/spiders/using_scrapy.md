tutorial ref: https://thepythonscrapyplaybook.com/scrapy-beginners-guide/


# step 1: create project 
## scrapy startproject <name_of_project>


# step 2: create a scrapy spider:  scrapy genspider pwd/cregslist_spider <website_irl>

# step 3: add  "shell=ipython" to scrapy.cfg


# step 4 : run the scarpy shell : scrapy shell 
     - fetch the website "fetch ("https://vancouver.craigslist.org/search/apa#search=2~gallery~40")"
     - see scrapy shell options: shelp()

# step 5: pull tags from the stored reponse 
     - look for tags in the file response.css("div.class_name").get()

# step 6: move all the response.css() into spider  parse section, use start_request() to call to link you need
     def start_request(self):
          yield scrapy.Request(self.start_request, callback=self.parse) #callback - which method to hit next, put response.css in there. 
     
# step 7: spider/setting.py enable pipeline to process data



## testing spider
/home/chris/Desktop/4260_presentation/Modules/spiders/cregslist_spider

scrapy crawl cregslist_spider
 


### default object is installed via the requirements and the import in to the spider/ whereever is 

from spider_default_obj.spider_default_obj import Post_Data