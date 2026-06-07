"""
REW Real Estate Scraper

Purpose:
    Scrape property listings from REW.ca and convert them into
    structured ListingObject instances.

Current Features:
    - Listing URL extraction
    - Price extraction
    - Bedrooms extraction
    - Bathrooms extraction
    - Square footage extraction
    - Lot size extraction
    - Property type extraction
    - Address formatting
    - Address component separation
    - CSV export support

Future Features:
    - Agent extraction
    - Brokerage extraction
    - Listing detail page scraping
    - Amenities extraction
    - Historical listing tracking
"""

import requests
from bs4 import BeautifulSoup
from datetime import datetime

import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parents[3]))

from Modules.spiders.spider_default_obj.spider_std_obj import SpiderData_Default_Obj

import re

def format_address(address):
    if address == "N/A":
        return "N/A"

    neighbourhoods = [
        "Kitsilano",
        "Marpole",
        "Arbutus",
        "Yaletown",
        "Knight",
        "Cambie",
        "Downtown West",
        "Downtown East",
        "Mount Pleasant East",
        "Mount Pleasant West",
        "Grandview East",
        "Hastings",
        "Main",
        "Fairview",
        "Coal Harbour",
        "West End",
        "False Creek",
        "Kerrisdale"
    ]

    formatted = address

    for neighbourhood in neighbourhoods:
        if neighbourhood in formatted:
            formatted = formatted.replace(
                f" {neighbourhood} Vancouver",
                f", {neighbourhood}, Vancouver, BC"
            )
            return formatted

    formatted = formatted.replace(" Vancouver", ", Vancouver, BC")
    return formatted

def split_address(address):
    if address == "N/A":
        return {
            "street_address": "N/A",
            "neighbourhood": "N/A",
            "city": "N/A",
            "province": "N/A"
        }

    parts = [part.strip() for part in address.split(",")]

    return {
        "street_address": parts[0] if len(parts) > 0 else "N/A",
        "neighbourhood": parts[1] if len(parts) > 1 else "N/A",
        "city": parts[2] if len(parts) > 2 else "N/A",
        "province": parts[3] if len(parts) > 3 else "N/A"
    }

def extract_price(text):
    match = re.search(r"\$[\d,]+", text)
    return match.group(0) if match else "N/A"


def extract_address(text):
    text = re.sub(r"^(V Tour|Virtual Tour|Open \w+|Follow)\s+", "", text)
    text = text.replace("Follow Follow", "").strip()

    match = re.search(
        r"\$[\d,]+\s+(.*?)\s+\d+\s+bd",
        text
    )

    return match.group(1).strip() if match else "N/A"


def extract_bedrooms(text):
    match = re.search(r"(\d+)\s+bd", text)
    return match.group(1) if match else "N/A"


def extract_bathrooms(text):
    match = re.search(r"(\d+)\s+ba", text)
    return match.group(1) if match else "N/A"


def extract_square_feet(text):
    match = re.search(r"(\d+)\s+sf", text)
    return match.group(1) if match else "N/A"

def extract_lot_size(text):
    match = re.search(r"(\d+\s+x\s+\d+\s+ft)", text)
    return match.group(1) if match else "N/A"


def extract_property_type(text):
    property_types = ["Apt/Condo", "Townhouse", "Duplex", "House"]

    for property_type in property_types:
        if property_type.lower() in text.lower():
            return property_type

    return "N/A"

def extract_agent_and_brokerage(text):
    """
    Extract agent name and brokerage from the listing text.

    This is a simple first version based on the text that appears
    after the property type.
    """

    property_type = extract_property_type(text)

    if property_type == "N/A":
        return "N/A", "N/A"

    after_property_type = text.split(property_type, 1)[-1].strip()

    brokerage_keywords = [
        "RE/MAX",
        "Oakwyn",
        "Dexter",
        "Stilhavn",
        "Macdonald",
        "Engel",
        "Sutton",
        "Royal LePage",
        "eXp",
        "FaithWilson",
        "Christies",
        "Century 21",
        "Multiple Realty",
        "Prompton",
        "TRG"
    ]

    for keyword in brokerage_keywords:
        if keyword.lower() in after_property_type.lower():
            index = after_property_type.lower().find(keyword.lower())

            agent_name = after_property_type[:index].strip()
            brokerage = after_property_type[index:].strip()

            agent_name = agent_name.replace("PREC*", "").strip()
            brokerage = brokerage.replace("PREC*", "").strip()

            return agent_name if agent_name else "N/A", brokerage if brokerage else "N/A"

    return after_property_type, "N/A"


class RealEstateScraper:
    """
    Base real estate scraper.
    """

    def __init__(self, start_url):
        self.start_url = start_url

    def fetch(self):
        headers = {
            "User-Agent": "Mozilla/5.0"
        }

        response = requests.get(
            self.start_url,
            headers=headers,
            timeout=15
        )

        response.raise_for_status()

        return response.text

    def parse(self, html):
        soup = BeautifulSoup(html, "html.parser")

        listings = []

        cards = soup.find_all("article")

        for card in cards:
            title = card.get_text(" ", strip=True)

            link_tag = card.find("a", href=True)
            listing_url = link_tag["href"] if link_tag else self.start_url

            if listing_url.startswith("/"):
                listing_url = "https://www.rew.ca" + listing_url

            formatted_address = format_address(
                extract_address(title)
            )

            address_parts = split_address(
                formatted_address
            )

            agent_name, brokerage = extract_agent_and_brokerage(title)

            listing = SpiderData_Default_Obj(
    title=title,
    price=extract_price(title),
    bedrooms=extract_bedrooms(title),
    bathrooms=extract_bathrooms(title),
    square_feet=extract_square_feet(title),
    property_type=extract_property_type(title),

    address=formatted_address,
    street_address=address_parts["street_address"],
    neighbourhood=address_parts["neighbourhood"],
    city=address_parts["city"],
    province=address_parts["province"],

    lot_size=extract_lot_size(title),

    features="N/A",
    facilities="N/A",
    agent_name=agent_name,
    brokerage=brokerage,

    listing_url=listing_url,
    source_website="REW.ca",

    first_seen=datetime.now().strftime("%Y-%m-%d"),
    last_seen=datetime.now().strftime("%Y-%m-%d"),
)

            listings.append(listing)

        return listings

    def run(self):
        html = self.fetch()
        return self.parse(html)