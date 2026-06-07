"""
Kijiji Rental Listing Object

Represents a single rental listing scraped from Kijiji Vancouver.
Designed to match the project's ListingObject pattern used by REW spider.
"""

from dataclasses import dataclass, field
from datetime import datetime


@dataclass
class KijijiListingObject:
    """
    Data object representing a single Kijiji rental listing.

    Fields are grouped by:
        - Core listing info
        - Location (for map integration)
        - Unit details
        - Pricing
        - Metadata
    """

    # == Core listing info ==
    title: str = "N/A"
    listing_url: str = "N/A"
    listing_id: str = "N/A"
    source_website: str = "Kijiji.ca"

    # == Location (for map integration) ==
    address: str = "N/A"
    neighbourhood: str = "N/A"
    city: str = "Vancouver"
    province: str = "BC"
    latitude: str = "N/A"
    longitude: str = "N/A"

    # == Unit details ==
    bedrooms: str = "N/A"
    bathrooms: str = "N/A"
    square_feet: str = "N/A"
    property_type: str = "N/A"
    furnished: str = "N/A"
    pets_allowed: str = "N/A"
    parking: str = "N/A"
    utilities_included: str = "N/A"

    # == Pricing ==
    price: str = "N/A"

    # == Metadata ==
    description: str = "N/A"
    first_seen: str = field(default_factory=lambda: datetime.now().strftime("%Y-%m-%d"))
    last_seen: str = field(default_factory=lambda: datetime.now().strftime("%Y-%m-%d"))
    is_active: bool = True

    def to_dict(self) -> dict:
        """Convert listing to dictionary for DB storage or CSV export."""
        return {
            "title": self.title,
            "listing_url": self.listing_url,
            "listing_id": self.listing_id,
            "source_website": self.source_website,
            "address": self.address,
            "neighbourhood": self.neighbourhood,
            "city": self.city,
            "province": self.province,
            "latitude": self.latitude,
            "longitude": self.longitude,
            "bedrooms": self.bedrooms,
            "bathrooms": self.bathrooms,
            "square_feet": self.square_feet,
            "property_type": self.property_type,
            "furnished": self.furnished,
            "pets_allowed": self.pets_allowed,
            "parking": self.parking,
            "utilities_included": self.utilities_included,
            "price": self.price,
            "description": self.description,
            "first_seen": self.first_seen,
            "last_seen": self.last_seen,
            "is_active": self.is_active,
        }
