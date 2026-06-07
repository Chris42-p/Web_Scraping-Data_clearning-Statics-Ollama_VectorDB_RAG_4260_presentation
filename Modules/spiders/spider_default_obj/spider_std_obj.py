"""
Spider Standard Object

This is the default object all spiders should use to store listing data.
All spider objects should be mapped into this class before saving to the central DB.

Updated by: Yung (Philip)
- Fixed __init__ parameter list to match all self.xxx fields
- Added default values for optional fields
- Added to_dict() for DB/CSV storage
"""

import hashlib


class SpiderData_Default_Obj():
    def __init__(self,
        # Required fields
        title,
        listing_url,
        source_website,
        first_seen,
        last_seen,
        status,
        address,
        street_address,
        neighbourhood,
        city,
        province,
        price,
        bedrooms,
        bathrooms,
        square_feet,
        lot_size,
        property_type,
        features,
        facilities,
        agent_name,
        brokerage,

        # Optional fields (default N/A)
        img_of_unit="N/A",
        days_ago_posted="N/A",
        post_updated="N/A",
        post_description="N/A",
        move_in_date="N/A",
        security_deposit="N/A",
        min_rental_period="N/A",
        amenities="N/A",       # fixed typo: amenties → amenities
        pet="N/A",
        appliances="N/A",      # laundry, stove, dishwasher, washer, dryer
        parking="N/A",
        locker="N/A",
        smoking="N/A",
    ):
        # == Meta: about the post
        self.title = title
        self.listing_url = listing_url
        self.source_website = source_website
        self.img_of_unit = img_of_unit

        # == Market speed
        self.days_ago_posted = days_ago_posted
        self.post_updated = post_updated
        self.first_seen = first_seen
        self.last_seen = last_seen
        self.status = status

        # == Address of the home
        self.address = address
        self.street_address = street_address
        self.neighbourhood = neighbourhood
        self.city = city
        self.province = province

        # == About the unit
        self.price = price
        self.bedrooms = bedrooms
        self.bathrooms = bathrooms
        self.square_feet = square_feet
        self.lot_size = lot_size
        self.property_type = property_type
        self.post_description = post_description
        self.move_in_date = move_in_date
        self.security_deposit = security_deposit
        self.min_rental_period = min_rental_period

        # == Features
        self.amenities = amenities      # fixed typo: amenties → amenities
        self.features = features
        self.facilities = facilities
        self.pet = pet
        self.appliances = appliances    # laundry, stove, dishwasher, washer, dryer
        self.parking = parking
        self.locker = locker
        self.smoking = smoking

        # == Seller info
        self.agent_name = agent_name
        self.brokerage = brokerage

    def get_hash(self) -> str:
        """Generate unique hash from listing URL."""
        return hashlib.md5(self.listing_url.encode()).hexdigest()

    def to_dict(self) -> dict:
        """Convert to dictionary for DB/CSV storage."""
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
            "price": self.price,
            "bedrooms": self.bedrooms,
            "bathrooms": self.bathrooms,
            "square_feet": self.square_feet,
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
        }
