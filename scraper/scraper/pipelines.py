# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface

# This is file where i added custom pipelines for my Scrapy project.
import sqlite3
import logging
from itemadapter import ItemAdapter


logger = logging.getLogger(__name__)
 

# This file defines two pipelines for the Scrapy project: ValidationPipeline and SQLitePipeline.
class ValidationPipeline:

    REQUIRED_FIELDS = ("model", "name", "registration")
 
    @classmethod
    def from_crawler(cls, crawler):
        return cls()
 
# The ValidationPipeline is responsible for validating the scraped items. 
# It checks that the required fields (model, name, registration) are present and not empty. 
# If any of these fields are missing or empty, the item is dropped and a warning is logged. 
# Additionally, it attempts to clean and convert the mileage field to an integer, and normalizes the fuel field to lowercase. 
# This ensures that only valid and well-formed data is passed on to the next stage of the pipeline, which in this case is saving to SQLite.
    def process_item(self, item, spider):
        adapter = ItemAdapter(item)
        for field in self.REQUIRED_FIELDS:
            value = adapter.get(field)
            if not value or not str(value).strip():
                from scrapy.exceptions import DropItem
                logger.warning(
                    "Отброшен Item: пустое поле '%s' | URL: %s",
                    field,
                    adapter.get("detail_url", "unknown"),
                )
                raise DropItem(f"Empty required field: {field!r}")
 
        raw_mileage = adapter.get("mileage")
        if raw_mileage is not None:
            try:
                cleaned = "".join(c for c in str(raw_mileage) if c.isdigit())
                adapter["mileage"] = int(cleaned) if cleaned else None
            except (ValueError, TypeError):
                logger.warning(
                    "Не удалось очистить mileage: %r -> None", raw_mileage
                )
                adapter["mileage"] = None

        raw_fuel = adapter.get("fuel")
        if raw_fuel:
            adapter["fuel"] = str(raw_fuel).strip().lower()
 
        return item
 
# The SQLitePipeline is responsible for saving the validated items into a SQLite database. 
# It connects to the database when the spider opens, creates a table if it doesn't exist,
# and then inserts each item into the table while ensuring that duplicate entries (based on the registration field) are ignored.
# It also includes error handling for database operations and logs the actions taken, such as when an item is saved or when a duplicate is skipped.
class SQLitePipeline:
    def __init__(self, db_path):
        self.db_path = db_path
        self.conn = None
        self.cursor = None
 
    @classmethod
    def from_crawler(cls, crawler):
        db_path = crawler.settings.get("SQLITE_DB_PATH", "bmw_cars.db")
        return cls(db_path=db_path)

    def open_spider(self, spider):
        self.conn = sqlite3.connect(self.db_path)
        self.cursor = self.conn.cursor()
        self._create_table()
        logger.info("SQLitePipeline: connected to DB '%s'", self.db_path)


    def _create_table(self):
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS bmw_cars (
                id           INTEGER PRIMARY KEY AUTOINCREMENT,
                registration TEXT    UNIQUE NOT NULL,
                model        TEXT    NOT NULL,
                name         TEXT    NOT NULL,
                mileage      INTEGER,
                registered   TEXT,
                engine       TEXT,
                range        TEXT,
                exterior     TEXT,
                fuel         TEXT,
                transmission TEXT,
                upholstery   TEXT,
                detail_url   TEXT
            )
        """)
        self.conn.commit()

    def process_item(self, item, spider):
        adapter = ItemAdapter(item)
 
        try:
            self.cursor.execute(
                """
                INSERT OR IGNORE INTO bmw_cars
                    (registration, model, name, mileage, registered,
                     engine, range, exterior, fuel, transmission,
                     upholstery, detail_url)
                VALUES
                    (:registration, :model, :name, :mileage, :registered,
                     :engine, :range, :exterior, :fuel, :transmission,
                     :upholstery, :detail_url)
                """,
                {
                    "registration": adapter.get("registration"),
                    "model":        adapter.get("model"),
                    "name":         adapter.get("name"),
                    "mileage":      adapter.get("mileage"),
                    "registered":   adapter.get("registered"),
                    "engine":       adapter.get("engine"),
                    "range":        adapter.get("range"),
                    "exterior":     adapter.get("exterior"),
                    "fuel":         adapter.get("fuel"),
                    "transmission": adapter.get("transmission"),
                    "upholstery":   adapter.get("upholstery"),
                    "detail_url":   adapter.get("detail_url"),
                },
            )
            self.conn.commit()
 
            if self.cursor.rowcount == 0:
                logger.debug(
                    "SQLitePipeline: duplicate missed -> %s %s [%s]",
                    adapter.get("model"), adapter.get("name"), adapter.get("registration"),
                )
            else:
                logger.debug(
                    "SQLitePipeline: saved -> %s %s [%s]",
                    adapter.get("model"), adapter.get("name"), adapter.get("registration"),
                )
 
        except sqlite3.Error as exc:
            logger.error("SQLitePipeline: ошибка БД -> %s", exc)

        return item
    
    def close_spider(self, spider):
        if self.conn:
            self.conn.close()
            logger.info("SQLitePipeline: connection closed")
