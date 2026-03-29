# Define here the models for your spider middleware
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/spider-middleware.html

import random
import logging
from scrapy import signals

logger = logging.getLogger(__name__)
 

# This is file where i added custom middlewares for my Scrapy project. 
# It includes a middleware to randomize the User-Agent header for each request, 
# as well as standard spider and downloader middlewares that can be customized further if needed. 
# The RandomUserAgentMiddleware helps to mimic different browsers and reduce the chances of being blocked by the target website.

class RandomUserAgentMiddleware:

    USER_AGENTS = [
        (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/122.0.0.0 Safari/537.36"
        ),
        (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:124.0) "
            "Gecko/20100101 Firefox/124.0"
        ),
        (
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 14_4) "
            "AppleWebKit/605.1.15 (KHTML, like Gecko) "
            "Version/17.3.1 Safari/605.1.15"
        ),
        (
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/122.0.0.0 Safari/537.36"
        ),
        (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/122.0.0.0 Safari/537.36 Edg/122.0.0.0"
        ),
        (
            "Mozilla/5.0 (X11; Linux x86_64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/122.0.0.0 Safari/537.36"
        ),
        (
            "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:124.0) "
            "Gecko/20100101 Firefox/124.0"
        ),
    ]
    @classmethod
    def from_crawler(cls, crawler):
        instance = cls()
        instance.crawler = crawler
        return instance

    def process_request(self, request):
        user_agent = random.choice(self.USER_AGENTS)
        request.headers["User-Agent"] = user_agent
        logger.debug(
            "RandomUserAgentMiddleware: выбран User-Agent -> %s | URL: %s",
            user_agent,
            request.url,
        )
 

# Standard Spider and Downloader middlewares (templates) that can be further customized if needed. 
# They currently just pass through the data without modification, but they include hooks for processing spider output, 
# handling exceptions, and logging when the spider is opened. 
# These can be expanded to add additional functionality as required by the scraping project.

class BmwScraperSpiderMiddleware:
    @classmethod
    def from_crawler(cls, crawler):
        s = cls()
        crawler.signals.connect(s.spider_opened, signal=signals.spider_opened)
        return s
 
    def process_spider_output(self, response, result, spider):
        for i in result:
            yield i
 
    def process_spider_exception(self, response, exception, spider):
        pass
 
    def process_start_requests(self, start_requests, spider):
        for r in start_requests:
            yield r
 
    def spider_opened(self, spider):
        spider.logger.debug("Spider opened: %s" % spider.name)
 

# Standard Downloader Middleware (template) that can be further customized if needed. 
# It currently just passes through the requests and responses without modification, 
# but it includes hooks for processing requests, handling exceptions, and logging when the spider is opened. 
# This can be expanded to add additional functionality as required by the scraping project.

class BmwScraperDownloaderMiddleware:
    @classmethod
    def from_crawler(cls, crawler):
        s = cls()
        crawler.signals.connect(s.spider_opened, signal=signals.spider_opened)
        return s
 
    # ИСПРАВЛЕНИЕ: убран аргумент spider
    def process_request(self, request):
        return None
 
    def process_response(self, request, response, spider):
        return response
 
    def process_exception(self, request, exception, spider):
        pass
 
    def spider_opened(self, spider):
        spider.logger.debug("Spider opened: %s" % spider.name)