# Kijiji Spider Items
# Fields match SpiderData_Default_Obj from spider_default_obj module

import scrapy


class KijijiRentalItem(scrapy.Item):
    """
    Scrapy Item matching SpiderData_Default_Obj fields.
    Additional Kijiji-specific fields: listing_id, listing_hash, latitude, longitude.
    """

    # === Matching SpiderData_Default_Obj ===
    # Meta
    title = scrapy.Field()
    listing_url = scrapy.Field()
    source_website = scrapy.Field()
    img_of_unit = scrapy.Field()

    # Market speed
    days_ago_posted = scrapy.Field()
    post_updated = scrapy.Field()
    first_seen = scrapy.Field()
    last_seen = scrapy.Field()
    status = scrapy.Field()

    # Address
    address = scrapy.Field()
    street_address = scrapy.Field()
    neighbourhood = scrapy.Field()
    city = scrapy.Field()
    province = scrapy.Field()

    # Unit details
    price = scrapy.Field()
    bedrooms = scrapy.Field()
    bathrooms = scrapy.Field()
    square_feet = scrapy.Field()
    lot_size = scrapy.Field()
    property_type = scrapy.Field()
    post_description = scrapy.Field()
    move_in_date = scrapy.Field()
    security_deposit = scrapy.Field()
    min_rental_period = scrapy.Field()

    # Features
    amenities = scrapy.Field()
    features = scrapy.Field()
    facilities = scrapy.Field()
    pet = scrapy.Field()
    appliances = scrapy.Field()
    parking = scrapy.Field()
    locker = scrapy.Field()
    smoking = scrapy.Field()

    # Seller info
    agent_name = scrapy.Field()
    brokerage = scrapy.Field()

    # === Kijiji-specific ===
    listing_id = scrapy.Field()
    listing_hash = scrapy.Field()
    latitude = scrapy.Field()
    longitude = scrapy.Field()

    furnished = scrapy.Field()
    pets_allowed = scrapy.Field()
    utilities_included = scrapy.Field()
    description = scrapy.Field()
    is_active = scrapy.Field()
