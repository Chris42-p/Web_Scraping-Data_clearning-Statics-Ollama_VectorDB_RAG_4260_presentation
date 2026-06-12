"""
Kijiji Vancouver Rental Spider

Uses SpiderData_Default_Obj fields from spider_default_obj module.
Parses JSON-LD structured data for clean, structured fields.
Neighbourhood extracted from address or postal code lookup table.

Usage:
    cd Modules/spiders/kijiji_spider
    scrapy crawl kijiji_rentals
    scrapy crawl kijiji_rentals -O ../../../scraped_data/kijiji_rentals.csv
"""

import scrapy
import json
import re
import hashlib
from datetime import datetime

from kijiji_spider.items import KijijiRentalItem


# ===== Postal code → neighbourhood lookup =====

POSTAL_NEIGHBOURHOOD_MAP = {  
    # Vancouver
    "V5K": "Hastings-Sunrise",
    "V5L": "Grandview-Woodland",
    "V5M": "Renfrew-Collingwood",
    "V5N": "Kensington-Cedar Cottage",
    "V5P": "Victoria-Fraserview",
    "V5R": "Killarney",
    "V5S": "Killarney",
    "V5T": "Mount Pleasant",
    "V5V": "Riley Park",
    "V5W": "Marpole",
    "V5X": "Marpole",
    "V5Y": "Mount Pleasant",
    "V5Z": "Fairview",
    "V6A": "Strathcona",
    "V6B": "Downtown",
    "V6C": "Downtown",
    "V6E": "West End",
    "V6G": "West End",
    "V6H": "Fairview",
    "V6J": "Kitsilano",
    "V6K": "Kitsilano",
    "V6M": "Kerrisdale",
    "V6N": "Marpole",
    "V6P": "Sunset",
    "V6R": "Point Grey",
    "V6S": "Dunbar",
    "V6T": "UBC",
    "V6Z": "Yaletown",
    # Burnaby
    "V3J": "Burnaby",
    "V3K": "Burnaby",
    "V3N": "Burnaby",
    "V5A": "Burnaby",
    "V5B": "Burnaby",
    "V5C": "Burnaby",
    "V5E": "Burnaby",
    "V5G": "Burnaby",
    "V5H": "Burnaby",
    # North Vancouver
    "V7G": "North Vancouver",
    "V7H": "North Vancouver",
    "V7J": "North Vancouver",
    "V7K": "North Vancouver",
    "V7L": "North Vancouver",
    "V7M": "North Vancouver",
    "V7N": "North Vancouver",
    "V7P": "North Vancouver",
    "V7R": "North Vancouver",
    # Coquitlam
    "V3B": "Coquitlam",
    "V3C": "Coquitlam",
    "V3E": "Coquitlam",
    # Richmond
    "V6V": "Richmond",
    "V6W": "Richmond",
    "V6X": "Richmond",
    "V6Y": "Richmond",
    "V7A": "Richmond",
    "V7B": "Richmond",
    "V7C": "Richmond",
    "V7E": "Richmond",
    # Surrey
    "V3R": "Surrey",
    "V3S": "Surrey",
    "V3T": "Surrey",
    "V3V": "Surrey",
    "V3W": "Surrey",
    "V3X": "Surrey",
    "V3Z": "Surrey",
    # White Rock
    "V4B": "White Rock",
}


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
        "White Rock", "Langley", "Abbotsford", "New Westminster",
        "Port Moody", "Port Coquitlam", "Delta", "Maple Ridge",
    ]

    # Step 1: check known neighbourhood names in address
    for n in neighbourhoods:
        if n.lower() in address.lower():
            return n

    # Step 2: extract from postal code
    postal_match = re.search(r'\b(V\d[A-Z])\s*\d[A-Z]\d\b', address)
    if postal_match:
        prefix = postal_match.group(1)
        if prefix in POSTAL_NEIGHBOURHOOD_MAP:
            return POSTAL_NEIGHBOURHOOD_MAP[prefix]

    # Step 3: fallback — second component after comma
    parts = address.split(",")
    if len(parts) >= 2:
        second = parts[1].strip()
        if (second not in ["BC", "AB", "ON", "QC"]
                and not re.match(r"^V\d", second)
                and not re.match(r"^BC\s", second)
                and len(second) > 3):
            return second

    return "N/A"


def _extract_city(address: str) -> str:
    """Extract actual city from address, not just Vancouver."""
    cities = {
        "North Vancouver": "North Vancouver",
        "West Vancouver": "West Vancouver",
        "Burnaby": "Burnaby",
        "Richmond": "Richmond",
        "Surrey": "Surrey",
        "Coquitlam": "Coquitlam",
        "Port Coquitlam": "Port Coquitlam",
        "Port Moody": "Port Moody",
        "New Westminster": "New Westminster",
        "White Rock": "White Rock",
        "Langley": "Langley",
        "Abbotsford": "Abbotsford",
        "Delta": "Delta",
        "Maple Ridge": "Maple Ridge",
    }
    for city, name in cities.items():
        if city.lower() in address.lower():
            return name
    return "Vancouver"


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
    Parses JSON-LD structured data. Fields match SpiderData_Default_Obj.
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

                price = _clean_number(f"${price_raw}") if price_raw != "N/A" else None
                sqft = _clean_number(sqft_raw) if sqft_raw not in ["0", "N/A"] else None
                bedrooms = "Studio/Bachelor" if bedrooms_raw == "0" else bedrooms_raw

                listing_id = "N/A"
                if url != "N/A":
                    match = re.search(r"/(\d+)$", url)
                    if match:
                        listing_id = match.group(1)

                item = KijijiRentalItem(
                    # === SpiderData_Default_Obj fields ===
                    title=d.get("name", "N/A"),
                    listing_url=url,
                    source_website="Kijiji.ca",
                    img_of_unit="N/A",
                    days_ago_posted="N/A",
                    post_updated="N/A",
                    first_seen=datetime.now().strftime("%Y-%m-%d"),
                    last_seen=datetime.now().strftime("%Y-%m-%d"),
                    status="active",
                    address=address,
                    street_address=_extract_street_address(address),
                    neighbourhood=_extract_neighbourhood(address),
                    city=_extract_city(address),
                    province="BC",
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
                    amenities="N/A",
                    features="N/A",
                    facilities="N/A",
                    pet=_extract_pets(d.get("petsAllowed", "N/A")),
                    appliances="N/A",
                    parking="N/A",
                    locker="N/A",
                    smoking="N/A",
                    agent_name="N/A",
                    brokerage="N/A",
                    listing_id=listing_id,
                    listing_hash=hashlib.md5(url.encode()).hexdigest(),
                    latitude="N/A",
                    longitude="N/A",
                    furnished="N/A",
                    pets_allowed=_extract_pets(d.get("petsAllowed", "N/A")),
                    utilities_included="N/A",
                    description=description[:300] if description else "N/A",
                    is_active=1,
                )

                listings_found += 1
                yield item

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