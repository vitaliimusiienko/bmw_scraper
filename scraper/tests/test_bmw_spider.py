import pytest
from scrapy.http import HtmlResponse, Request

from scraper.spiders.bmw_spider import BmwSpider

@pytest.fixture
def spider():
    return BmwSpider()

def test_build_item(spider):

    fake_vehicle_data = {
        "title": "BMW X7",
        "derivative": "X7 xDrive40i M Sport",
        "mileage": 8465,
        "fuel": "petrol",
        "transmission": "Automatic",
        "identification": {"registration": "SV24GVL"},
        "registration": {"date": "2024-03-28"},
        "engine": {"cc": 2998},
        "advert_id": 202406291270447
    }

    item = spider._build_item(fake_vehicle_data)

    assert item["model"] == "BMW X7"
    assert item["name"] == "X7 xDrive40i M Sport"
    assert item["mileage"] == 8465
    assert item["fuel"] == "petrol"
    assert item["registration"] == "SV24GVL"
    assert item["registered"] == "Mar 2024"
    assert item["engine"] == "2,998 cc"
    assert item["detail_url"] == "https://usedcars.bmw.co.uk/vehicle/202406291270447"

def test_parse_specification(spider):

    fake_html = """
    <html>
        <head><title>Test BMW</title></head>
        <body>
            <script type="text/javascript">
                var UVL = window.UVL || {};
                UVL.AD = {
                    "colour": {"manufacturer_colour": "Brooklyn Grey"},
                    "specification": {"interior": "Black Sensafin Upholstery"},
                    "engine": {"size": {"cc": 2998}},
                    "consumption": {"range": {"values": {"total": null}}}
                };
                UVL.AOS_PLAYER = "test";
            </script>
        </body>
    </html>
    """

    request = Request(url="https://usedcars.bmw.co.uk/vehicle/123")
    response = HtmlResponse(url="https://usedcars.bmw.co.uk/vehicle/123", body=fake_html, encoding="utf-8", request=request)

    result = spider._parse_specification(response)

    assert result["exterior"] == "Brooklyn Grey"
    assert result["upholstery"] == "Black Sensafin Upholstery"
    assert result["engine"] == "2,998 cc"
    assert result["range"] is None

def test_get_csrf_from_cookie(spider):
    
    request = Request(url="https://usedcars.bmw.co.uk/result")
    headers = {
        b'Set-Cookie': [b'csrftoken=IhSISOVmFwllbavn2T0o1XjB6ijsCz3B; expires=Sun, 28 Mar 2027 16:21:41 GMT; Path=/']
    }
    response = HtmlResponse(url="https://usedcars.bmw.co.uk/result", headers=headers, request=request)

    token = spider._get_csrf_from_response(response)
    
    assert token == "IhSISOVmFwllbavn2T0o1XjB6ijsCz3B"