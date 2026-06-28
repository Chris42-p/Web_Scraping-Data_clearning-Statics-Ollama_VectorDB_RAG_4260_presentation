
#====== Libraries 
import scrapy
import math
import sys



#===== Interface
from ..realtylink_interface import CONST

#=== custom imports 
sys.path.append("/home/chris/Desktop/4260_presentation/Modules/spiders") #this is how to import std.obj



class RealtylinkSpiderSpider(scrapy.Spider):
    name = CONST["SPIDER_NAME"] #"realtylink_spider"
    allowed_domains = CONST["ALLOWED_DOMAINS"] #"realtylink.org"]
    start_urls =CONST["START_URL"] #["https://realtylink.org/en/properties~for-rent~vancouver?q=H4sIAAAAAAAACpWRzU7DMBCE38XngCJxgltUCYRAqCIoF8RhiSeNVccOaycQVX131i0_Iafik2f284xs71Rng7pSucrUK_steOU1xBDtm8bUuMN0lEPADfyGqW-nsqUeci7PVEjbyuBd5POLaBDX7QN1XymNsRGchjvVUazbp6lPo1VRFjKO-IiiKnK1H0awWEaLUXsXhk4Omoiz715TFwy6OB9_6L00NgZWh4rsgGPNwbjVvyVjmv0jNPuTQREbz9Ms5xHBaLhoyC7gEtYatznccc67uADX7HtwnFL3jCzfBmJcA0v-npw-lU11a5a_m8H5CczlbMnL7j8BoxVmmR0CAAA&v=2&sortSeed=1953928980&sort=None&pageSize=12&page=1"]

    first_loop=True
    total_pages=0
    page_num=0

    
    def start_requests(self):  
        for url in self.start_urls:  
            yield scrapy.Request(url, callback=self.parse) # one URL 

    def parse(self, response):
        #== Get card meta data
        posts=response.css("div#divMainResult div.property-thumbnail-item") #all the objects      

        #number of pages that i can itterate over. 
        num_posts=response.css("span.js-resultCount.font-weight-bold:nth-child(2)::text").get()
        total_pages=math.ceil(int(num_posts)/ len(posts))
        
        #===== the url of the cards on the page
        base_url="https://realtylink.org"
        for p_num in posts:
            url_of_a_post=p_num.css(f"div.shell:nth-child(1) a::attr(href)").get()

            url=f"{base_url}{url_of_a_post}"
            yield scrapy.Request(url, callback=self.parse_page)
        #read a card's data

        if self.first_loop:
            self.total_pages=total_pages
            self.first_loop=False


        #=== Read next page

        while (self.page_num <  self.total_pages):
            url=f"https://realtylink.org/en/properties~for-rent~vancouver?q=H4sIAAAAAAAACpWRzU7DMBCE38XngCJxgltUCYRAqCIoF8RhiSeNVccOaycQVX131i0_Iafik2f284xs71Rng7pSucrUK_steOU1xBDtm8bUuMN0lEPADfyGqW-nsqUeci7PVEjbyuBd5POLaBDX7QN1XymNsRGchjvVUazbp6lPo1VRFjKO-IiiKnK1H0awWEaLUXsXhk4Omoiz715TFwy6OB9_6L00NgZWh4rsgGPNwbjVvyVjmv0jNPuTQREbz9Ms5xHBaLhoyC7gEtYatznccc67uADX7HtwnFL3jCzfBmJcA0v-npw-lU11a5a_m8H5CczlbMnL7j8BoxVmmR0CAAA&v=2&sortSeed=1953928980&sort=None&pageSize=12&page={self.page_num}"
            self.page_num+=1
            
            yield scrapy.Request(url, callback=self.parse)


    def parse_page(self, response):
        unit_type=response.css("span[data-id='PageTitle']::text").get()
        unit_address= response.css("div.row.property-tagline div.col.text-left.pl-0 h2.pt-1::text").get() #across posts
        unit_price=response.css("meta[itemprop='price']::attr(content)").get()  #across posts
        sqr_feet=response.css("div.carac-value span::text").get() #across post
        description=response.css("div[itemprop='description']::text").get() #across post
        msl_numer=response.css("span#ListingDisplayId::text").get().strip() #across post
        bed=response.css("div.col-lg-3.col-sm-6.cac::text").get().strip() #across posts
        bath= response.css("div.col-lg-3.col-sm-6.sdb::text").get().strip()#across posts
        first_pic=response.css("div.primary-photo-container img::attr(src)").get() #across sites
        broker_agency= response.css("div.broker-info-office-info.col-12.col-md-8 h2.p1::text").get()
        
        #=== Meta fields ====
        property_metadata={ #not all fields are avialable on ever page 
            "Floor Area":None, 
            "Interior Features":None,
            "Laundry Features":None,
            "Appliances":None,
            "Exterior Features":None,
            "Parking Spaces":None,
            "Amenities":None,
            "Cooling Features":None,
            "Bylaws Restriction":None,
            
        }   
        
        for index in range(len(response.css("div.row div.col-lg-3.col-sm-6.carac-container"))):

            subheading_titles=response.css(f"div.row div.col-lg-3.col-sm-6.carac-container:nth-child({index}) div.carac-title::text").get()
            subheading_value=response.css(f"div.row div.col-lg-3.col-sm-6.carac-container:nth-child({index}) div.carac-value span::text").get()

            if subheading_titles in property_metadata:
                property_metadata[subheading_titles]=subheading_value
        
        yield{
            "url":response.url,
            "unit_address":unit_address,
            "unit_type":unit_type,
            "unit_price":unit_price,
            "sqr_feet":sqr_feet,
            "description":description,
            "msl_numer":msl_numer,
            "bed":bed,
            "bath":bath,
            "first_pic":first_pic,
            "property_metadata":property_metadata,
            "broker_agency":broker_agency,
        }