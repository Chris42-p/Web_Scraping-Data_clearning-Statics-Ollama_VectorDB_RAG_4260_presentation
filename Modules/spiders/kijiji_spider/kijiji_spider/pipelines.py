"""
Kijiji Spider Pipeline

Follows cregslist_spider pipeline pattern:
- Cleans raw scraped fields
- Maps into Post_Data from spider_default_obj
- Post_Data handles LLM parsing of post_description automatically
"""

import re
# from bs4 import BeautifulSoup

from kijiji_spider.spider_interface import CONST
# import sys, os
# sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'spider_default_obj'))
# from spider_default_obj import Post_Data

class KijijiSpiderPipeline:

    def process_item(self, item, spider):
        # TODO: map into Post_Data once DB structure is confirmed by Chris
        spider.logger.info(
            f"Item scraped: {item.get('post_id')} | "
            f"{item.get('user_post_title')} | "
            f"${item.get('price_of_the_unit')} | "
            f"{item.get('address')}"
        )
        return item

    def __extract_city(self, address: str) -> str:
        cities = [
            "North Vancouver", "West Vancouver", "Burnaby", "Richmond",
            "Surrey", "Coquitlam", "Port Coquitlam", "Port Moody",
            "New Westminster", "White Rock", "Langley", "Abbotsford",
            "Delta", "Maple Ridge",
        ]
        for city in cities:
            if city.lower() in str(address).lower():
                return city
        return "Vancouver"
