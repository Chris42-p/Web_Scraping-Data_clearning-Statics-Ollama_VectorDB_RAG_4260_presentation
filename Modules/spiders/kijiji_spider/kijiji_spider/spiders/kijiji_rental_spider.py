"""
Kijiji Vancouver Rental Spider

Uses SpiderData_Default_Obj from spider_default_obj module.
Fields mapped from Kijiji JSON-LD data.

Usage:
    cd Modules/spiders/kijiji_spider
    scrapy crawl kijiji_rentals
    scrapy crawl kijiji_rentals -O ../../../scraped_data/kijiji_rentals.csv
"""

import scrapy
import json
import re
import hashlib
import sys
from pathlib import Path
from datetime import datetime

from kijiji_spider.items import KijijiRentalItem

# Import shared spider object
sys.path.append(str(Path(__file__).parent.parent.parent.parent.parent))
try:
    from Modules.spiders.spider_default_obj.spider_std_obj import SpiderData_Default_Obj
except ImportError:
    SpiderData_Default_Obj = None


# ===== Private extraction helpers =====

def _clean_number(value):
    if value in ["N/A", None, "Studio/Bachelor"]:
        return None
    cleaned = re.sub(r"[^\d.]", "", str(value))
    return int(float(cleaned)) if cleaned else None


def _extract_street_address(address: str) -> str:
    if not address or address == "N/A":
        return "N/A"
    if "," in address:
        return address.split(",")[0].strip()
    return address.strip()


def _extract_neighbourhood(address: str) -> str:
    if not address or address == "N/A":
        return "N/A"

    neighbourhoods = [
        "Kitsilano", "Marpole", "Arbutus", "Yaletown", "Knight", "Cambie",
        "Downtown", "Mount Pleasant", "Grandview", "Hastings", "Main",
        "Fairview", "Coal Harbour", "West End", "False Creek", "Kerrisdale",
        "Strathcona", "Renfrew", "Collingwood", "Oakridge", "Riley Park",
        "Sunset", "Victoria", "Dunbar", "Point Grey", "Shaughnessy",
        "South Cambie", "Kensington", "Cedar Cottage", "Fraserview",
        "Killarney", "Champlain Heights", "Hastings-Sunrise", "East Village",
        "Metrotown", "Burnaby", "Richmond", "Surrey", "North Vancouver",
        "Coquitlam", "Gastown", "Chinatown", "UBC", "Lonsdale",
    ]
    for n in neighbourhoods:
        if n.lower() in address.lower():
            return n

    parts = address.split(",")
    if len(parts) >= 2:
        second = parts[1].strip()
        if second not in ["BC", "AB", "ON"] and not re.match(r"^V\d", second):
            return second
    return "N/A"


def _extract_property_type(description: str, bedrooms: str) -> str:
    types = {
        "Apartment": ["apartment", "condo", "apt", "unit"],
        "House": ["house", "home", "detached", "single family"],
        "Townhouse": ["townhouse", "townhome"],
        "Basement Suite": ["basement", "suite"],
        "Room": ["room for rent", "bedroom in", "shared"],
        "Studio": ["studio", "bachelor"],
        "Duplex": ["duplex"],
    }
    lower = (description or "").lower()
    for prop_type, keywords in types.items():
        if any(kw in lower for kw in keywords):
            return prop_type
    if bedrooms == "0":
        return "Studio"
    return "N/A"


def _extract_pets(pets_raw: str) -> str:
    return {"true": "Yes", "false": "No"}.get(str(pets_raw).lower(), "N/A")


# ===== Spider =====

class KijijiRentalsSpider(scrapy.Spider):
    """
    Scrapy spider for Kijiji Vancouver rental listings.
    Parses JSON-LD structured data. Uses SpiderData_Default_Obj.
    """

    name = "kijiji_rentals"
    allowed_domains = ["kijiji.ca"]
    start_urls = ["https://www.kijiji.ca/b-apartments-condos/vancouver/c37l1700287"]

    def __init__(self, max_pages=3, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.max_pages = int(max_pages)
        self.current_page = 1

    def parse(self, response):
        scripts = response.css('script[type="application/ld+json"]::text').getall()
        listings_found = 0

        for script in scripts:
            try:
                data = json.loads(script)
            except json.JSONDecodeError:
                continue

            if data.get("@type") != "ItemList":
                continue

            items = data.get("itemListElement", [])
            self.logger.info(f"Page {self.current_page}: found {len(items)} listings")

            for entry in items:
                d = entry.get("item", {})

                url = d.get("url", "N/A")
                address = d.get("address", "N/A")
                description = d.get("description", "N/A")
                bedrooms_raw = str(d.get("numberOfBedrooms", "N/A"))
                price_raw = d.get("offers", {}).get("price", "N/A")
                sqft_raw = str(d.get("floorSize", {}).get("value", "N/A"))

                # Format fields
                price = _clean_number(f"${price_raw}") if price_raw != "N/A" else None
                sqft = _clean_number(sqft_raw) if sqft_raw not in ["0", "N/A"] else None
                bedrooms = "Studio/Bachelor" if bedrooms_raw == "0" else bedrooms_raw

                # listing ID from URL
                listing_id = "N/A"
                if url != "N/A":
                    match = re.search(r"/(\d+)$", url)
                    if match:
                        listing_id = match.group(1)

                item = KijijiRentalItem(
                    # === Matching SpiderData_Default_Obj fields ===
                    title=d.get("name", "N/A"),
                    listing_url=url,
                    source_website="Kijiji.ca",
                    img_of_unit="N/A",

                    # Market speed
                    days_ago_posted="N/A",
                    post_updated="N/A",
                    first_seen=datetime.now().strftime("%Y-%m-%d"),
                    last_seen=datetime.now().strftime("%Y-%m-%d"),
                    status="active",

                    # Address
                    address=address,
                    street_address=_extract_street_address(address),
                    neighbourhood=_extract_neighbourhood(address),
                    city="Vancouver",
                    province="BC",

                    # Unit details
                    price=price,
                    bedrooms=bedrooms,
                    bathrooms=str(d.get("numberOfBathroomsTotal", "N/A")),
                    square_feet=sqft,
                    lot_size="N/A",
                    property_type=_extract_property_type(description, bedrooms_raw),
                    post_description=description[:300] if description else "N/A",
                    move_in_date="N/A",
                    security_deposit="N/A",
                    min_rental_period="N/A",

                    # Features
                    amenities="N/A",
                    features="N/A",
                    facilities="N/A",
                    pet=_extract_pets(d.get("petsAllowed", "N/A")),
                    appliances="N/A",
                    parking="N/A",
                    locker="N/A",
                    smoking="N/A",

                    # Seller info
                    agent_name="N/A",
                    brokerage="N/A",

                    # Kijiji-specific
                    listing_id=listing_id,
                    listing_hash=hashlib.md5(url.encode()).hexdigest(),
                    latitude="N/A",
                    longitude="N/A",
                )

                listings_found += 1
                yield item

        # Pagination
        if self.current_page < self.max_pages and listings_found > 0:
            self.current_page += 1
            next_url = (
                "https://www.kijiji.ca/b-apartments-condos/vancouver/"
                f"page-{self.current_page}/c37l1700287"
            )
            yield scrapy.Request(
                url=next_url,
                callback=self.parse,
                headers={"Referer": response.url},
            )
