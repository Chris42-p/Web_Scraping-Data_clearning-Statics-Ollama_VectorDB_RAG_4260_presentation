"""
Standard Spider Data Object

This object defines the default output format for all spiders.
Every spider should map its scraped data into this object before
saving to the database or sending data to analytics/ML modules.
"""

from dataclasses import dataclass
import hashlib
import re


def clean_number(value):
    if value in (None, "", "N/A"):
        return None

    cleaned = re.sub(r"[^\d.]", "", str(value))

    if cleaned == "":
        return None

    return int(float(cleaned))


@dataclass
class SpiderData_Default_Obj:
    # Meta
    title: str = "N/A"
    listing_url: str = "N/A"
    source_website: str = "N/A"
    img_of_unit: str = "N/A"

    # Market speed
    days_ago_posted: str = "N/A"
    post_updated: str = "N/A"
    first_seen: str = "N/A"
    last_seen: str = "N/A"
    status: str = "active"

    # Address
    address: str = "N/A"
    street_address: str = "N/A"
    neighbourhood: str = "N/A"
    city: str = "N/A"
    province: str = "N/A"
    postal_code: str = "N/A"
    latitude: str = "N/A"
    longitude: str = "N/A"

    # Unit information
    price: str = "N/A"
    bedrooms: str = "N/A"
    bathrooms: str = "N/A"
    square_feet: str = "N/A"
    lot_size: str = "N/A"
    property_type: str = "N/A"
    post_description: str = "N/A"
    move_in_date: str = "N/A"
    security_deposit: str = "N/A"
    min_rental_period: str = "N/A"

    # Features
    amenities: str = "N/A"
    features: str = "N/A"
    facilities: str = "N/A"
    pet: str = "N/A"
    appliances: str = "N/A"
    parking: str = "N/A"
    locker: str = "N/A"
    smoking: str = "N/A"

    # Seller / listing info
    agent_name: str = "N/A"
    brokerage: str = "N/A"
    mls_number: str = "N/A"

    # Building info
    building_name: str = "N/A"
    building_age: str = "N/A"
    year_built: str = "N/A"

    def get_hash(self):
        return hashlib.md5(self.listing_url.encode()).hexdigest()

    def to_json(self):
        return {
            "listing_hash": self.get_hash(),
            "title": self.title,
            "listing_url": self.listing_url,
            "source_website": self.source_website,
            "img_of_unit": self.img_of_unit,

            "days_ago_posted": self.days_ago_posted,
            "post_updated": self.post_updated,
            "first_seen": self.first_seen,
            "last_seen": self.last_seen,
            "status": self.status,

            "address": self.address,
            "street_address": self.street_address,
            "neighbourhood": self.neighbourhood,
            "city": self.city,
            "province": self.province,
            "postal_code": self.postal_code,
            "latitude": self.latitude,
            "longitude": self.longitude,

            "price": clean_number(self.price),
            "bedrooms": clean_number(self.bedrooms),
            "bathrooms": clean_number(self.bathrooms),
            "square_feet": clean_number(self.square_feet),
            "lot_size": self.lot_size,
            "property_type": self.property_type,
            "post_description": self.post_description,
            "move_in_date": self.move_in_date,
            "security_deposit": self.security_deposit,
            "min_rental_period": self.min_rental_period,

            "amenities": self.amenities,
            "features": self.features,
            "facilities": self.facilities,
            "pet": self.pet,
            "appliances": self.appliances,
            "parking": self.parking,
            "locker": self.locker,
            "smoking": self.smoking,

            "agent_name": self.agent_name,
            "brokerage": self.brokerage,
            "mls_number": self.mls_number,

            "building_name": self.building_name,
            "building_age": self.building_age,
            "year_built": self.year_built,
        }