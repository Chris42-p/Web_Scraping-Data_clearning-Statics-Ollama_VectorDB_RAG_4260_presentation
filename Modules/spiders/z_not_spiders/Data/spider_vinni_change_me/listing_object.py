"""
Listing Object Module

This module defines the ListingObject class used by the real estate scraper.
Each ListingObject represents one property listing collected from a website.

The object also provides:
- a unique hash based on the listing URL
- a JSON/dictionary representation for CSV storage
- numeric cleaning for fields used in analysis
"""

from dataclasses import dataclass
import hashlib
import re

def clean_number(value):

    """
    Convert formatted text values into integers.

    Examples:
        "$1,688,000" -> 1688000
        "3" -> 3
        "N/A" -> None
    """

    if value == "N/A" or value is None:
        return None

    cleaned = re.sub(r"[^\d.]", "", str(value))

    if cleaned == "":
        return None

    return int(float(cleaned))


@dataclass
class ListingObject:

    """
    Represents one real estate listing.

    This class stores both raw listing information and structured fields
    that can later be used for analysis, such as price, bedrooms,
    bathrooms, square footage, neighbourhood, and property type.
    """

    title: str
    price: str
    address: str
    street_address: str
    neighbourhood: str
    city: str
    province: str
    bedrooms: str
    bathrooms: str
    square_feet: str
    lot_size: str
    property_type: str
    features: str
    facilities: str
    agent_name: str
    brokerage: str
    listing_url: str
    source_website: str
    first_seen: str
    last_seen: str
    status: str = "active"

    def get_hash(self):

        return hashlib.md5(self.listing_url.encode()).hexdigest()

    def to_json(self):

        """
        Convert the ListingObject into a dictionary.

        This format is used by the CSV storage class and can later
        be reused for database insertion or vector embedding.
        """

        return {
            "listing_hash": self.get_hash(),
            "title": self.title,
            "price": clean_number(self.price),
            "address": self.address,
            "street_address": self.street_address,
            "neighbourhood": self.neighbourhood,
            "city": self.city,
            "province": self.province,
            "bedrooms": clean_number(self.bedrooms),
            "bathrooms": clean_number(self.bathrooms),
            "square_feet": clean_number(self.square_feet),
            "lot_size": self.lot_size,
            "property_type": self.property_type,
            "features": self.features,
            "facilities": self.facilities,
            "agent_name": self.agent_name,
            "brokerage": self.brokerage,
            "listing_url": self.listing_url,
            "source_website": self.source_website,
            "first_seen": self.first_seen,
            "last_seen": self.last_seen,
            "status": self.status
        }