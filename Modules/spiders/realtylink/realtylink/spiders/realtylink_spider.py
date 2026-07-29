
#====== Libraries 
import scrapy
import math
import sys



#===== Interface
from ..realtylink_interface import CONST


#== IMPORT THE DEFUALT OBJECT DYNAMICALLY =====
from pathlib import Path
import sys

# walk up until we find the folder that contains 'Modules'
current = Path(__file__).resolve()
for parent in current.parents:
    if (parent / "Modules").exists():
        sys.path.append(str(parent))
        break

from Modules.spiders.spider_default_obj.spider_default_obj import Post_Data
#==========================


#this is going to scrape websites for data. 
class RealtylinkSpiderSpider(scrapy.Spider):
    name = CONST["SPIDER_NAME_WEB_CRAWLER"] #"realtylink_spider"
    allowed_domains = CONST["ALLOWED_DOMAINS"] #"realtylink.org"]
    start_urls =CONST["START_URL"] 

    first_loop=True
    total_pages=0
    page_num=0

    
    def start_requests(self):  
        for url in self.start_urls:  
            yield scrapy.Request(url, callback=self.parse) # one URL 

    def parse(self, response):
        posts = response.css("div#divMainResult div.property-thumbnail-item")

        if not posts:
            self.logger.warning(f"No posts found on {response.url}")
            return

        for post in posts:
            rel = post.css("div.shell a::attr(href)").get()
            if rel:
                yield response.follow(rel, callback=self.parse_page)

        if self.first_loop:
            self.first_loop = False

            num_posts_text = response.css(
                "span.js-resultCount.font-weight-bold:nth-child(2)::text"
            ).get(default="0").strip()

            try:
                num_posts = int(num_posts_text.replace(",", ""))
                total_pages = math.ceil(num_posts / len(posts))
            except ValueError:
                self.logger.warning(f"Could not parse result count: {num_posts_text}")
                return

            for page_num in range(2, total_pages + 1):
                url = f"https://realtylink.org/en/properties~for-rent~vancouver?q=H4sIAAAAAAAACpWRzU7DMBCE38XngCJxgltUCYRAqCIoF8RhiSeNVccOaycQVX131i0_Iafik2f284xs71Rng7pSucrUK_steOU1xBDtm8bUuMN0lEPADfyGqW-nsqUeci7PVEjbyuBd5POLaBDX7QN1XymNsRGchjvVUazbp6lPo1VRFjKO-IiiKnK1H0awWEaLUXsXhk4Omoiz715TFwy6OB9_6L00NgZWh4rsgGPNwbjVvyVjmv0jNPuTQREbz9Ms5xHBaLhoyC7gEtYatznccc67uADX7HtwnFL3jCzfBmJcA0v-npw-lU11a5a_m8H5CczlbMnL7j8BoxVmmR0CAAA&v=2&sortSeed=1953928980&sort=None&pageSize=12&page={page_num}"
                yield scrapy.Request(url, callback=self.parse)


    def parse_page(self, response):
        if "listingnotfound=" in response.url:
            self.logger.info(f"Skipping removed listing: {response.url}")
            return

        unit_type = response.css("span[data-id='PageTitle']::text").get(default="").strip() or None
        unit_address = response.css(
            "div.row.property-tagline div.col.text-left.pl-0 h2.pt-1::text"
        ).get(default="").strip() or None
        unit_price = response.css("meta[itemprop='price']::attr(content)").get(default="").strip() or None
        sqr_feet = response.css("div.carac-value span::text").get(default="").strip() or None
        description = " ".join(
            t.strip() for t in response.css("div[itemprop='description'] *::text").getall() if t.strip()
        ) or None
        msl_numer = response.css("span#ListingDisplayId::text").get(default="").strip() or None
        bed = response.css("div.col-lg-3.col-sm-6.cac::text").get(default="").strip() or None
        bath = response.css("div.col-lg-3.col-sm-6.sdb::text").get(default="").strip() or None
        first_pic = response.css("div.primary-photo-container img::attr(src)").get(default="").strip() or None
        broker_agency = response.css(
            "div.broker-info-office-info.col-12.col-md-8 h2.p1::text"
        ).get(default="").strip() or None

        property_metadata = {
            "Floor Area": None,
            "Interior Features": None,
            "Laundry Features": None,
            "Appliances": None,
            "Exterior Features": None,
            "Parking Spaces": None,
            "Amenities": None,
            "Cooling Features": None,
            "Bylaws Restriction": None,
        }

        for container in response.css("div.row div.col-lg-3.col-sm-6.carac-container"):
            subheading_title = container.css("div.carac-title::text").get(default="").strip()
            subheading_value = " ".join(
                t.strip() for t in container.css("div.carac-value *::text").getall() if t.strip()
            ) or None

            if subheading_title in property_metadata:
                property_metadata[subheading_title] = subheading_value

        yield {
            "url": response.url,
            "unit_address": unit_address,
            "unit_type": unit_type,
            "unit_price": unit_price,
            "sqr_feet": sqr_feet,
            "description": description,
            "msl_numer": msl_numer,
            "bed": bed,
            "bath": bath,
            "first_pic": first_pic,
            "property_metadata": property_metadata,
            "broker_agency": broker_agency,
        }


