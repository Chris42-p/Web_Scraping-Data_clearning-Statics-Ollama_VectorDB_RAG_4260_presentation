"""
Kijiji Spider Pipeline

Follows cregslist_spider pipeline pattern:
- Cleans raw scraped fields
- Maps into Post_Data from spider_default_obj
- Post_Data handles LLM parsing of post_description automatically

Post_Data __init__ parameter order (as of latest spider_default_obj.py):
    post_id, time_of_post, user_post_title, first_pic, user_meta_tags,
    post_url, price_of_the_unit, sqr_feet, general_area, street_number,
    city, province, postal_code, bed, bath, square_feet_unit,
    post_description, rent_period, leasing_agent, source_spider, img_url
"""

import re
import time
from pathlib import Path
import sys
from geopy.geocoders import Nominatim
import time

from .spider_interface import CONST

VANCOUVER_AREAS = [
    "Vancouver", "North Vancouver", "West Vancouver", "Burnaby", "Richmond",
    "Surrey", "Coquitlam", "Port Coquitlam", "Port Moody", "New Westminster",
    "White Rock", "Langley", "Abbotsford", "Delta", "Maple Ridge", "Squamish",
    "Pitt Meadows", "Mission", "Chilliwack",
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

    def __init__(self):
        try:
            from geopy.geocoders import Nominatim
            self._geolocator = Nominatim(user_agent="kijiji_spider_pipeline")
            self._geo_available = True
        except ImportError:
            self._geolocator = None
            self._geo_available = False

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

        # == first_pic / img_url
        first_img_url = item.get("first_pic", "N/A")
        if isinstance(first_img_url, (list, tuple)):
            first_img_url = str(first_img_url[0]) if first_img_url else "N/A"
        else:
            first_img_url = str(first_img_url) if first_img_url not in (None, "") else "N/A"

        # == user_meta_tags
        user_meta_tags = item.get("user_meta_tags", "N/A")

        # == post_url
        post_url = item.get("post_url", "N/A")

        # == price — Kijiji returns cents, divide by 100
        price_raw = str(item.get("price_of_the_unit", "N/A"))
        price_cleaned = re.sub(r"[^\d.]", "", price_raw)
        if price_cleaned:
            try:
                price_of_the_unit = str(int(float(price_cleaned) / 100))
            except ValueError:
                price_of_the_unit = "N/A"
        else:
            price_of_the_unit = "N/A"

        # == sqr_feet (bedrooms count from spider)
        sqr_feet = str(item.get("num_bedrooms_n_square_feet_sq", "N/A"))
        if sqr_feet == "0":
            sqr_feet = "Studio/Bachelor"

        # == general_area — fuzzy matched to known Vancouver areas
        general_area = self.__extract_city(item.get("city_general_area", "N/A"))

        # == address parsing
        address_raw = item.get("address", "N/A")
        street_number, city, province, postal_code = self.__process_address(address_raw)

        # == if postal code missing, try geopy lookup
        if postal_code in ("N/A", "", None):
            postal_code = self.__get_postal_code(address_raw, spider)

        # == bed / bath
        bed, bath = self.__get_bed_bath(item)

        # == square_feet_unit
        sqft_raw = str(item.get("square_feet_unit", "N/A"))
        square_feet_unit = re.sub(r"[^\d]", "", sqft_raw) or "N/A"

        # == post_description
        post_description = item.get("post_description", "N/A")
        if str(post_description).strip() in ("None", "(None,)", "N/A", "", "none"):
            post_description = None
            
        # == rent_period
        rent_period = item.get("rent_period", "monthly")

        # == leasing_agent
        leasing_agent = item.get("leasing_agent", "N/A")

        latitude, longitude, address_osm = self.__geocode_address(
            street_number,
            city,
            province,
            postal_code,
        )
        time.sleep(1)

        Post_Data(
            post_id=str(post_id),
            time_of_post=str(time_of_post),
            user_post_title=str(user_post_title),
            first_pic=str(first_img_url),
            user_meta_tags=str(user_meta_tags),
            post_url=str(post_url),
            price_of_the_unit=str(price_of_the_unit),
            sqr_feet=str(sqr_feet),
            general_area=str(general_area),
            street_number=str(street_number),
            city=str(city),
            province=str(province),
            postal_code=str(postal_code),
            latitude=latitude,
            longitude=longitude,
            address_osm=address_osm,
            bed=str(bed),
            bath=str(bath),
            square_feet_unit=str(square_feet_unit),
            post_description=str(post_description) if post_description not in (None, "N/A") else None,
            rent_period=str(rent_period),
            leasing_agent=str(leasing_agent),
            source_spider=str(spider.name),
            img_url=str(first_img_url),
        ).save_new_post_to_db()

        return item

    def __geocode_address(self, street_number, city, province, postal_code):
        parts = [street_number, city, province, postal_code, "Canada"]
        query = ", ".join([part for part in parts if part and part != "N/A"])

        try:
            geolocator = Nominatim(user_agent="housing_scraper_geocoder")
            location = geolocator.geocode(query, timeout=10)
            if not location:
                return None, None, None

            return float(location.latitude), float(location.longitude), location.address
        except Exception as exc:
            print(f"Geocode failed for '{query}': {exc}")
            return None, None, None

    def __get_postal_code(self, address: str, spider) -> str:
        """
        Use geopy Nominatim to reverse-geocode a full address string
        and extract the postal code.
        Rate limit: 1 request/second (Nominatim free tier).
        Returns "N/A" if geocoding fails or postal code not found.
        """
        if not self._geo_available or not address or address == "N/A":
            return "N/A"

        try:
            time.sleep(1)
            location = self._geolocator.geocode(
                f"{address}, Canada",
                addressdetails=True,
                timeout=5,
            )
            if location and location.raw.get("address"):
                addr = location.raw["address"]
                postal = addr.get("postcode", "N/A")
                spider.logger.debug(f"[geopy] {address} -> {postal}")
                return postal or "N/A"
        except Exception as e:
            spider.logger.debug(f"[geopy] Failed for '{address}': {e}")

        return "N/A"

    def __get_bed_bath(self, item):
        bed_bath_str = item.get("bed_and_bath")
        if not bed_bath_str:
            return "N/A", "N/A"

        x = bed_bath_str.split("/")
        bed_match  = re.search(r'\d+', x[0]) if len(x) > 0 else None
        bath_match = re.search(r'\d+', x[1]) if len(x) > 1 else None

        bed  = bed_match.group()  if bed_match  else "N/A"
        bath = bath_match.group() if bath_match else "N/A"

        return bed, bath

    def __process_address(self, address: str):
        if not address or address == "N/A":
            return "N/A", "N/A", "N/A", "N/A"
        try:
            parts = address.split(",")
            street_number   = parts[0].strip() if len(parts) > 0 else "N/A"
            city            = parts[1].strip() if len(parts) > 1 else "N/A"
            province_postal = parts[2].strip() if len(parts) > 2 else ""
            province_parts  = province_postal.split(" ")
            province        = province_parts[0] if province_parts else "N/A"
            postal_code     = " ".join(province_parts[1:]) if len(province_parts) > 1 else "N/A"
            return street_number, city, province, postal_code
        except Exception:
            return address, "N/A", "N/A", "N/A"

    def __extract_city(self, raw: str) -> str:
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