import scrapy


class RewSpiderItem(scrapy.Item):
    post_id = scrapy.Field()
    time_of_post = scrapy.Field()
    user_post_title = scrapy.Field()
    first_pic = scrapy.Field()
    user_meta_tags = scrapy.Field()
    post_url = scrapy.Field()

    price_of_the_unit = scrapy.Field()
    num_bedrooms_n_square_feet_sq = scrapy.Field()
    city_general_area = scrapy.Field()
    address = scrapy.Field()
    bed_and_bath = scrapy.Field()
    square_feet_unit = scrapy.Field()

    post_description = scrapy.Field()
    rent_period = scrapy.Field()
    leasing_agent = scrapy.Field()

    latitude = scrapy.Field()
    longitude = scrapy.Field()