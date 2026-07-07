import sys
from pathlib import Path

#== IMPORT THE DEFUALT OBJECT DYNAMICALLY =====
from pathlib import Path
import sys
import re

# walk up until we find the folder that contains 'Modules'
current = Path(__file__).resolve()
for parent in current.parents:
    if (parent / "Modules").exists():
        sys.path.append(str(parent))
        break

from Modules.spiders.spider_default_obj.spider_default_obj import Post_Data


class RewSpiderPipeline:

    def process_item(self, item, spider):

        post_id = item.get("post_id", "N/A")
        time_of_post = item.get("time_of_post", "N/A")
        user_post_title = item.get("user_post_title", "N/A")
        first_pic = item.get("first_pic", "N/A")
        user_meta_tags = item.get("user_meta_tags", "N/A")
        post_url = item.get("post_url", "N/A")

        price_of_the_unit = item.get("price_of_the_unit", "N/A")
        sqr_feet = item.get("num_bedrooms_n_square_feet_sq", "N/A")
        general_area = item.get("city_general_area", "N/A")

        address = item.get("address", "N/A")
        street_number, city, province, postal_code = self.__process_address(address)

        bed,bath = self.__get_bed_bath(item)
        square_feet_unit = item.get("square_feet_unit", "N/A")
        post_description = item.get("post_description", "N/A")
        rent_period = item.get("rent_period", "monthly")
        leasing_agent = item.get("leasing_agent", "N/A")

        spider.logger.info(
            f"Saving REW item: {post_id} | {user_post_title}"
        )

        Post_Data(
            post_id,
            time_of_post,
            user_post_title,
            first_pic,
            user_meta_tags,
            post_url,
            price_of_the_unit,
            sqr_feet,
            general_area,
            street_number,
            city,
            province,
            postal_code,
            bed,
            bath,
            square_feet_unit,
            post_description,
            rent_period,
            leasing_agent,
            source_spider=spider.name,
        ).save_new_post_to_db()

        return item
    
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