import scrapy


class BmwSpiderSpider(scrapy.Spider):
    name = "bmw_spider"
    allowed_domains = ["usedcars.bmw.co.uk"]
    start_urls = ["https://usedcars.bmw.co.uk/result/?payment_type=cash&size=23&source=home"]

    def parse(self, response):
        pass
