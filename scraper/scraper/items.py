import scrapy


class BMWItem(scrapy.Item):
    model = scrapy.Field() # BMW model
    name = scrapy.Field() # Name of the car
    mileage = scrapy.Field() # Mileage of the car
    registered = scrapy.Field() # Year of registration
    engine = scrapy.Field() # Engine size
    range = scrapy.Field() # Range of the car
    exterior = scrapy.Field() # Exterior color
    fuel = scrapy.Field() # Fuel type
    transmission = scrapy.Field() # Transmission type
    registration = scrapy.Field() # Registration number
    upholstery = scrapy.Field() # Upholstery type
    detail_url = scrapy.Field() # URL of the car details page
