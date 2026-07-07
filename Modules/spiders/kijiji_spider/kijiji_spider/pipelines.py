"""
Kijiji Spider Pipeline

Follows cregslist_spider pipeline pattern:
- Cleans raw scraped fields
- Maps into Post_Data from spider_default_obj
- Post_Data handles LLM parsing of post_description automatically

save_new_post_to_db() parameter order (as of latest spider_default_obj.py):
    post_id, time_of_post, user_post_title, user_meta_tags, post_url,
    price_of_the_unit, sqr_feet_lot, general_area, street_number, city,
    province, postal_code, bed, bath, square_feet_unit, post_description,
    rent_period, leasing_agent, first_img_url
"""

import re
from pathlib import Path
import sys

from kijiji_spider.spider_interface import CONST

# Known Vancouver cities and neighbourhoods for general_area normalization.
VANCOUVER_AREAS = [
    # Cities / municipalities
    "Vancouver", "North Vancouver", "West Vancouver", "Burnaby", "Richmond",
    "Surrey", "Coquitlam", "Port Coquitlam", "Port Moody", "New Westminster",
    "White Rock", "Langley", "Abbotsford", "Delta", "Maple Ridge", "Squamish",
    "Pitt Meadows", "Mission", "Chilliwack",
    # Vancouver neighbourhoods
    "Downtown Vancouver", "Downtown", "West End", "Yaletown", "Gastown",
    "Chinatown", "Mount Pleasant", "Fairview", "Kitsilano", "Point Grey",
    "Dunbar", "Kerrisdale", "Marpole", "South Granville", "Cambie",
    "Riley Park", "Sunset", "Victoria", "Hastings", "East Vancouver",
    "Commercial Drive", "Grandview", "Renfrew", "Collingwood", "Fraserview",
    "Killarney", "Champlain Heights", "Oakridge", "Shaughnessy",
    "Arbutus Ridge", "West Side", "East Side", "River District",
    "False Creek", "Coal Harbour", "Strathcona", "Main Street",
    "South Vancouver", "Metrotown", "Brentwood", "Lougheed",
    "Joyce", "Nanaimo", "Rupert", "Renfrew Heights",
]


class KijijiSpiderPipeline:

    def process_item(self, item, spider):

        # == Dynamically import Post_Data at runtime
        current = Path(__file__).resolve()
        for parent in current.parents:
            if (parent / "Modules").exists():
                if str(parent) not in sys.path:
                    sys.path.append(str(parent))
                break
        from Modules.spiders.spider_default_obj.spider_default_obj import Post_Data

        # == post_id
        post_id = str(item.get("post_id", "N/A")).strip()

        # == time_of_post
        time_of_post = item.get("time_of_post", "N/A")

        # == user_post_title
        user_post_title = item.get("user_post_title", "N/A")

        # == first_pic
        first_img_url = item.get("first_pic", "N/A")

        # == user_meta_tags
        user_meta_tags = item.get("user_meta_tags", "N/A")

        # == post_url
        post_url = item.get("post_url", "N/A")

        # == price — strip to number only
        price_raw = str(item.get("price_of_the_unit", "N/A"))
        price_of_the_unit = re.sub(r"[^\d.]", "", price_raw) or "N/A"

        # == general_area — fuzzy matched to known Vancouver areas
        general_area = self.__extract_city(item.get("city_general_area", "N/A"))

        # == address parsing — split into components
        address_raw = item.get("address", "N/A")
        street_number, city, province, postal_code = self.__process_address(address_raw)

        # == bed / bath
        bed, bath = self.__get_bed_bath(item)

        # == square_feet_unit
        sqft_raw = str(item.get("square_feet_unit", "N/A"))
        square_feet_unit = re.sub(r"[^\d]", "", sqft_raw) or "N/A"

        # == post_description
        post_description = item.get("post_description", "N/A")

        # == rent_period
        rent_period = item.get("rent_period", "monthly")

        # == leasing_agent
        leasing_agent = item.get("leasing_agent", "N/A")

        # == sqr_feet_lot — not available on Kijiji rentals
        sqr_feet_lot = item.get("sqr_feet_lot", "N/A")

        Post_Data().save_new_post_to_db(
            post_id=post_id,
            time_of_post=time_of_post,
            user_post_title=user_post_title,
            user_meta_tags=user_meta_tags,
            post_url=post_url,
            price_of_the_unit=price_of_the_unit,
            sqr_feet_lot=sqr_feet_lot,
            general_area=general_area,
            street_number=street_number,
            city=city,
            province=province,
            postal_code=postal_code,
            bed=bed,
            bath=bath,
            square_feet_unit=square_feet_unit,
            post_description=post_description,
            rent_period=rent_period,
            leasing_agent=leasing_agent,
            first_img_url=first_img_url,
            source_spider=spider.name,
        )

        return item

    def __get_bed_bath(self, item):
        bed_bath_str = item.get("bed_and_bath")
        if not bed_bath_str:
            return "N/A", "N/A"

        x = bed_bath_str.split("/")
        bed_match = re.search(r'\d+', x[0]) if len(x) > 0 else None
        bath_match = re.search(r'\d+', x[1]) if len(x) > 1 else None

        bed = bed_match.group() if bed_match else "N/A"
        bath = bath_match.group() if bath_match else "N/A"

        return bed, bath

    def __process_address(self, address: str):
        if not address or address == "N/A":
            return "N/A", "N/A", "N/A", "N/A"
        try:
            parts = address.split(",")
            street_number = parts[0].strip() if len(parts) > 0 else "N/A"
            city = parts[1].strip() if len(parts) > 1 else "N/A"
            province_postal = parts[2].strip() if len(parts) > 2 else ""
            province_parts = province_postal.split(" ")
            province = province_parts[0] if province_parts else "N/A"
            postal_code = " ".join(province_parts[1:]) if len(province_parts) > 1 else "N/A"
            return street_number, city, province, postal_code
        except Exception:
            return address, "N/A", "N/A", "N/A"

    def __extract_city(self, raw: str) -> str:
        """
        Normalize general_area to a known Vancouver city or neighbourhood.
        Uses rapidfuzz for fuzzy matching to handle variations like:
        - "VANCOUVER WEST SIDE" -> "West Vancouver"
        - "SOUTH GRANVILLE" -> "South Granville"
        - "24XX E 29TH AVE" -> "Vancouver" (fallback)
        """
        if not raw or raw == "N/A":
            return "Vancouver"

        try:
            from rapidfuzz import process, fuzz
            result = process.extractOne(
                raw,
                VANCOUVER_AREAS,
                scorer=fuzz.token_set_ratio,
                score_cutoff=80,
            )
            if result:
                return result[0]
        except ImportError:
            for area in VANCOUVER_AREAS:
                if area.lower() in raw.lower():
                    return area

        return "Vancouver"