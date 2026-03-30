import json
import re
import scrapy

from scraper.items import BMWItem


# Spider to scrape used BMW cars from usedcars.bmw.co.uk. 
# It first scrapes the listing page to get a CSRF token, 
# then makes API requests to get the list of vehicles, 
# and finally visits each vehicle's detail page to extract additional information like exterior color and upholstery. 
# The spider is designed to scrape a maximum of 5 pages of results for testing purposes.

class BmwSpider(scrapy.Spider):
    name = "bmw_spider"
    allowed_domains = ["usedcars.bmw.co.uk"]
    start_urls = ["https://usedcars.bmw.co.uk/result/?payment_type=cash&size=23&source=home"]

    API_LIST = "https://usedcars.bmw.co.uk/vehicle/api/list/"

    MAX_PAGES = 5

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.pages_scraped = 0 # Counter to track how many pages have been scraped

    def parse(self, response):
        self.logger.info(f"Scraping page {self.pages_scraped + 1} of {self.MAX_PAGES}")
        self.logger.debug(f"Response URL: {response.url}")
        
        self.csrf_token = self._get_csrf_from_response(response)
        if self.csrf_token:
            self.logger.info("CSRF token extracted successfully")
        else:
            self.logger.warning("Failed to extract CSRF token, API requests may fail")
            return
        yield self._make_api_request(page=1)
    

    # This method tries multiple strategies to extract the CSRF token from the response, 
    # including cookies, meta tags, and inline JavaScript.
    def _get_csrf_from_response(self, response):
        for cookie_header in response.headers.getlist("Set-Cookie"):
            cookie_str = cookie_header.decode("utf-8", errors="ignore")
            m = re.search(r"csrftoken=([^;,\s]+)", cookie_str)
            if m:
                return m.group(1)
            
        meta_token = response.css('meta[name="csrf-token"]::attr(content)').get()
        if meta_token:
            return meta_token
        
        for script in response.css("script::text").getall():
            m = re.search(r'"csrfToken"\s*:\s*"([^"]+)"', script)
            if m:
                return m.group(1)
            
        return None

    # This method constructs the API request URL with the appropriate query parameters and headers, including the CSRF token.    
    def _make_api_request(self, page):
        url = (
            f"{self.API_LIST}"
            f"?payment_type=cash"
            f"&size={self.MAX_PAGES}"
            f"&page={page}"
            f"&source=home"
        )

        return scrapy.Request(
            url=url,
            callback=self._parse_api,
            cb_kwargs={"page": page},
            headers={
                "accept": "application/json, text/plain, */*",
                "accept-language": "en-GB,en;q=0.9",
                "referer": "https://usedcars.bmw.co.uk/result/?payment_type=cash&size=23&source=home",
                "sec-fetch-dest": "empty",
                "sec-fetch-mode": "cors",
                "sec-fetch-site": "same-origin",
                "x-csrftoken": self.csrf_token,
                   },
            dont_filter=True,
        )
    
    # This method handles the API response, checks for errors, and processes the list of vehicles. 
    # It also logs the number of vehicles received and yields requests for the detail pages of each vehicle.
    def _parse_api(self, response, page):
        if response.status in (400, 403):
            try:
                err = json.loads(response.text)
                self.logger.error("API error %d: %s", response.status, err.get("detail", "No detail"))

            except json.JSONDecodeError:
                self.logger.error("HTTP %d: %s", response.status, response.text[:200])
            return
        
        try:
            data = json.loads(response.text)
        except json.JSONDecodeError as e:
            self.logger.error("Failed to parse JSON response: %s", e)
            return
        
        if not data.get("success", True):
            self.logger.error("API success=False: %s", data.get("message", ""))
            return
        
        vehicles = data.get("results", [])

        self.pages_scraped += 1
 
        self.logger.info("Received %d vehicles (page %d of %d)", len(vehicles), self.pages_scraped, self.MAX_PAGES)

        for vehicle in vehicles[:self.MAX_PAGES]:
            item = self._build_item(vehicle)
            if item and item.get("detail_url"):
                yield scrapy.Request(
                    url=item["detail_url"],
                    callback=self.parse_detail,
                    cb_kwargs={"item": item},
                    headers={"referer": response.request.headers.get('referer', b'').decode('utf-8')},
                )
            elif item:
                yield item

    # This method takes the raw vehicle data from the API response and constructs a BMWItem with the relevant fields.
    def _build_item(self, v):
        item = BMWItem()

        item["model"] = v.get("title", "").strip() or None

        item["name"] = v.get("derivative", "").strip() or None

        item["mileage"] = v.get("mileage")

        item["fuel"] = v.get("fuel", "").strip() or None

        item["transmission"] = v.get("transmission", "").strip() or None

        identification = v.get("identification", {})
        item["registration"] = identification.get("registration", "").strip() or None

        reg_obj = v.get("registration", {})
        item["registered"] = self._format_date(reg_obj.get("date", ""))

        cc = v.get("engine", {}).get("cc", 0)
        item["engine"] = f"{cc:,} cc" if cc and cc > 0 else None

        fuel_lower = (item["fuel"] or "").lower()
        total_range = v.get("consumption", {}).get("range", {}).get("values", {}).get("total")
        item["range"] = f"{total_range} miles" if "electric" in fuel_lower and total_range else None

        item["exterior"] = None
        item["upholstery"] = None

        advert_id = v.get("advert_id")
        item["detail_url"] = f"https://usedcars.bmw.co.uk/vehicle/{advert_id}" if advert_id else None
 
        return item
    
    # This method takes an ISO date string (e.g. "2020-05-01") and formats it as "May 2020". 
    # If the input is not in the expected format, it returns the original string.
    @staticmethod
    def _format_date(iso_date):
        if not iso_date:
            return None
        months = {
            "01": "Jan", "02": "Feb", "03": "Mar", "04": "Apr",
            "05": "May", "06": "Jun", "07": "Jul", "08": "Aug",
            "09": "Sep", "10": "Oct", "11": "Nov", "12": "Dec",
        }
        m = re.match(r"(\d{4})-(\d{2})-", iso_date)
        if m:
            return f"{months.get(m.group(2), m.group(2))} {m.group(1)}"
        return iso_date
    
    # This method takes the response from the vehicle detail page and the partially filled item, 
    # extracts additional specifications such as exterior color and upholstery, and updates the item before yielding it.
    def parse_detail(self, response, item):
        spec = self._parse_specification(response)

        item["exterior"]   = spec.get("exterior colour") or spec.get("exterior") or spec.get("colour")
        item["upholstery"] = spec.get("upholstery") or spec.get("interior") or spec.get("trim")

        if not item.get("engine"):
            item["engine"] = spec.get("engine") or spec.get("engine size")
        if not item.get("range"):
            item["range"] = spec.get("range") or spec.get("electric range")

        self.logger.info(
             "Parsed details for %s %s: exterior=%s, upholstery=%s",
            item.get("model"), item.get("name"),
            item.get("exterior"), item.get("upholstery"),
        )
        yield item

    # This method looks for a JavaScript variable named UVL.AD in the page source, which contains a JSON object with the vehicle's specifications. 
    # It uses a regular expression to extract this JSON data, parses it, and then retrieves
    def _parse_specification(self, response):
        result = {
            "exterior": None, 
            "upholstery": None, 
            "engine": None, 
            "range": None
        }
        
        match = re.search(r'UVL\.AD\s*=\s*(\{.*?\});\s*UVL\.', response.text, re.DOTALL)
        
        if match:
            try:
                data = json.loads(match.group(1))
                colour_data = data.get("colour") or {}
                result["exterior"] = colour_data.get("manufacturer_colour") or colour_data.get("colour")

                spec_data = data.get("specification") or {}
                result["upholstery"] = spec_data.get("interior")

                engine_data = data.get("engine") or {}
                size_data = engine_data.get("size") or {}
                engine_cc = size_data.get("cc")
                if engine_cc:
                    result["engine"] = f"{engine_cc:,} cc"

                consumption_data = data.get("consumption") or {}
                range_data = consumption_data.get("range") or {}
                values_data = range_data.get("values") or {}
                total_range = values_data.get("total")
                if total_range:
                    result["range"] = f"{total_range} miles"
                    
                self.logger.debug("Parsed specification data: %s", result)
                
            except json.JSONDecodeError as e:
                self.logger.error("Failed to parse JSON from page: %s", e)
        else:
            self.logger.warning("Failed to find UVL.AD data in page")

        return result