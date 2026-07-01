import scrapy

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


class StatusCheckerSpider(scrapy.Spider):
    name = CONST["SPIDER_NAME_STATUS_CHECKER"]
    allowed_domains = CONST["ALLOWED_DOMAINS"]
    start_urls = CONST["START_URL"]

    def parse(self, response):
        
        post_=Post_Data()
        rows=post_.get_urls()

        for row in rows:
            row_id, post_url, scraped_at= row[0],row[1],row[2]

            if "realtylink" not in post_url:
                continue

            #send a request to the website 
            yield scrapy.Request(post_url,
                                callback=self.check_status,
                                cb_kwargs={#args into method
                                    "row_id":row_id,
                                    "scraped_at":scraped_at
                                }
                                )               


    def check_status(self,response, row_id, scraped_at):
        active_post=None

        #post is expired    ------assuming the post is given a 404
        # response.css(alert alert-warning mt-2 mb-2)

        redirect=response.status==302 
        post_down=response.css("div.alert.alert-warning.mt-2.mb-2::text").get()=='\n            This property is no longer available. Here are other similar properties in the same area.\n        '
        
        if redirect and post_down:
            active_post=False
        else:
            active_post=True

        Post_Data().update_post_last_active(scraped_at,active_post,row_id )
