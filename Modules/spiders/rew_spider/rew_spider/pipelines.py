from pathlib import Path
import sys
import re

from geopy.geocoders import Nominatim
import time

# == Import default object dynamically ==
current = Path(__file__).resolve()
for parent in current.parents:
    if (parent / "Modules").exists():
        sys.path.append(str(parent))
        break

from Modules.spiders.spider_default_obj.spider_default_obj import Post_Data


class RewSpiderPipeline:
    def process_item(self, item, spider):
        post_id = item.get("post_id", "N/A")
        address = item.get("address", "N/A")
        street_number, city, province, postal_code = self.__process_address(address)
        bed, bath = self.__get_bed_bath(item)

        post = Post_Data()

        post.post_id = post_id
        post.time_of_post = item.get("time_of_post", "N/A")
        post.user_post_title = item.get("user_post_title", "N/A")
        post.first_pic = item.get("first_pic", "N/A")
        post.user_meta_tags = item.get("user_meta_tags", "N/A")
        post.post_url = item.get("post_url", "N/A")

        post.price_of_the_unit = item.get("price_of_the_unit", "N/A")
        post.sqr_feet = item.get("num_bedrooms_n_square_feet_sq", "N/A")
        post.square_feet_unit = item.get("square_feet_unit", "N/A")

        post.general_area = item.get("city_general_area", "N/A")
        post.street_number = street_number
        post.city = city
        post.province = province
        post.postal_code = postal_code

        post.latitude = item.get("latitude")
        post.longitude = item.get("longitude")
        post.address_osm = address

        post.bed = bed
        post.bath = bath
        post.post_description = item.get("post_description", "N/A")
        post.rent_period = item.get("rent_period", "monthly")
        post.leasing_agent = item.get("leasing_agent", "N/A")
        post.source_spider = spider.name
        post.img_url = item.get("first_pic", "N/A")

        post.save_new_post_to_db()
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

    def __get_bed_bath(self, item):
        bed_bath = item.get("bed_and_bath")
        if not bed_bath or bed_bath == "N/A":
            return "N/A", "N/A"

        parts = bed_bath.split("/")

        bed_match = re.search(r"\d+", parts[0]) if len(parts) > 0 else None
        bath_match = re.search(r"\d+", parts[1]) if len(parts) > 1 else None

        bed = int(bed_match.group()) if bed_match else "N/A"
        bath = int(bath_match.group()) if bath_match else "N/A"

        return bed, bath

    def __process_address(self, address):
        if not address or address == "N/A":
            return "N/A", "N/A", "N/A", "N/A"

        parts = [part.strip() for part in address.split(",")]

        street_number = parts[0] if len(parts) > 0 else "N/A"
        city = parts[2] if len(parts) > 2 else "N/A"
        province = parts[3] if len(parts) > 3 else "N/A"
        postal_code = "N/A"

        return street_number, city, province, postal_code