import scrapy
import math
import sys

#=== custom imports 
sys.path.append("/home/chris/Desktop/4260_presentation/Modules/spiders") #this is how to import std.obj


class RealtylinkSpiderSpider(scrapy.Spider):
    name = "realtylink_spider"
    allowed_domains = ["realtylink.org"]
    start_urls = ["https://realtylink.org/en/properties~for-rent~vancouver?q=H4sIAAAAAAAACpWRzU7DMBCE38XngCJxgltUCYRAqCIoF8RhiSeNVccOaycQVX131i0_Iafik2f284xs71Rng7pSucrUK_steOU1xBDtm8bUuMN0lEPADfyGqW-nsqUeci7PVEjbyuBd5POLaBDX7QN1XymNsRGchjvVUazbp6lPo1VRFjKO-IiiKnK1H0awWEaLUXsXhk4Omoiz715TFwy6OB9_6L00NgZWh4rsgGPNwbjVvyVjmv0jNPuTQREbz9Ms5xHBaLhoyC7gEtYatznccc67uADX7HtwnFL3jCzfBmJcA0v-npw-lU11a5a_m8H5CczlbMnL7j8BoxVmmR0CAAA&v=2&sortSeed=1953928980&sort=None&pageSize=12&page=1"]

    first_loop=True
    total_pages=0
    page_num=0

    
    def start_requests(self):  
        for url in self.start_urls:  
            yield scrapy.Request(url, callback=self.parse) # one URL 


    def parse(self, response):
        #== Get card meta data
        cards=response.css("div#divMainResult div.property-thumbnail-item") #all the objects      
        num_posts=response.css("span.js-resultCount.font-weight-bold:nth-child(2)::text").get()
        total_pages=math.ceil(int(num_posts)/ len(cards))

        #===== the url of the cards on the page
        base_url="https://realtylink.org"
        for card_num in len(cards):
            unit_card_url=  response.css(f"div.shell:nth-child({card_num}) a::attr(href)").get()     #== read the content in every post
            url=f"{base_url}{unit_card_url}"
            yield scrapy.Request(url, callback=self.__parse_page())
        #read a card's data

        if self.first_loop:
            self.total_pages=total_pages
            self.first_loop=False


        #=== Read next page

        while (self.page_num <  self.total_pages):
            url=f"https://realtylink.org/en/properties~for-rent~vancouver?q=H4sIAAAAAAAACpWRzU7DMBCE38XngCJxgltUCYRAqCIoF8RhiSeNVccOaycQVX131i0_Iafik2f284xs71Rng7pSucrUK_steOU1xBDtm8bUuMN0lEPADfyGqW-nsqUeci7PVEjbyuBd5POLaBDX7QN1XymNsRGchjvVUazbp6lPo1VRFjKO-IiiKnK1H0awWEaLUXsXhk4Omoiz715TFwy6OB9_6L00NgZWh4rsgGPNwbjVvyVjmv0jNPuTQREbz9Ms5xHBaLhoyC7gEtYatznccc67uADX7HtwnFL3jCzfBmJcA0v-npw-lU11a5a_m8H5CczlbMnL7j8BoxVmmR0CAAA&v=2&sortSeed=1953928980&sort=None&pageSize=12&page={self.page_num}"
            self.page_num+=1
            
            yield scrapy.Request(url, callback=self.parse)




    def __parse_page(self, response):
        unit_address= response.css(" div.row.property-tagline div.col.text-left.pl-0 h2.pt-1::text ").get()  #across posts
        unit_price=response.css("meta[itemprop='price']::attr(content)").get()  #across posts
        sqr_feet=response.css("div.carac-value span::text").get() #across post
        description=response.css("div[itemprop='description']::text").get() #across post
        msl_numer=response.css("span#ListingDisplayId::text").get().strip() #across post
        bed=response.css("div.col-lg-3.col-sm-6.cac::text").get().strip() #across posts
        bath= response.css("div.col-lg-3.col-sm-6.sdb::text").get().strip() #across posts
        first_pic=response.css("div.primary-photo-container img::attr(src)").get() #across sites
        # broker_name= #p1 m-0 broker-info__agency-name  #figure out later


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
        
        for index in len( response.css("div.row div.col-lg-3.col-sm-6.carac-container")):
            subheading_titles=response.css(f"div.row div.col-lg-3.col-sm-6.carac-container:nth-child({index}) div.carac-title::text").get()
            subheading_value=response.css(f"div.row div.col-lg-3.col-sm-6.carac-container:nth-child({index}) div.carac-value span::text").get()

            if subheading_titles in property_metadata:
                property_metadata[subheading_titles]=subheading_value
