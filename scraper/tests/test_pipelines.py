import sqlite3
import pytest
from scrapy.exceptions import DropItem

from scraper.pipelines import ValidationPipeline, SQLitePipeline
from scraper.items import BMWItem

class MockSpider:
    name = "test_spider"

@pytest.fixture
def valid_item():
    item = BMWItem()
    item["model"] = "BMW X7"
    item["name"] = "X7 xDrive40i M Sport"
    item["registration"] = "TEST1234"
    item["detail_url"] = "https://test.com/car"
    return item

@pytest.fixture
def invalid_item():
    item = BMWItem()
    item["model"] = "BMW X7"
    item["name"] = "X7 xDrive40i M Sport"
    item["registration"] = None
    item["detail_url"] = None
    return item

def test_validation_pipeline_passes_good_item(valid_item):
    pipeline = ValidationPipeline()
    spider = MockSpider()

    result = pipeline.process_item(valid_item, spider)
    assert result == valid_item

def test_validation_pipeline_drops_bad_item(invalid_item):
    pipeline = ValidationPipeline()
    spider = MockSpider()

    with pytest.raises(DropItem):
        pipeline.process_item(invalid_item, spider)

@pytest.fixture
def sqlite_pipeline():
    pipeline = SQLitePipeline(db_path=":memory:")
    spider = MockSpider()

    pipeline.open_spider(spider)
    
    yield pipeline

    pipeline.close_spider(spider)

def test_sqlite_pipeline_inserts_item(sqlite_pipeline, valid_item):
    spider = MockSpider()
    
    sqlite_pipeline.process_item(valid_item, spider)

    sqlite_pipeline.cursor.execute(
        "SELECT model, detail_url FROM bmw_cars WHERE registration = ?",
        (valid_item["registration"],)
        )
    
    row = sqlite_pipeline.cursor.fetchone()
    
    assert row is not None, "Car was not inserted into the database"
    assert row[0] == "BMW X7"
    assert row[1] == "https://test.com/car"