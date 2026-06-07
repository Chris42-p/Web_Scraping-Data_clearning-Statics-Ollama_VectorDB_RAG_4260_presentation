# Define your item pipelines here
#
# See https://docs.scrapy.org/en/latest/topics/item-pipeline.html

import sqlite3
import csv
from pathlib import Path
from datetime import datetime


class KijijiSpiderPipeline:
    """
    Item pipeline — processes each scraped item after the spider yields it.

    Currently:
        - Cleans and validates fields
        - Saves to SQLite database (table: kijiji_vancouver_rentals)
        - Exports to CSV

    To enable: uncomment ITEM_PIPELINES in settings.py
    """

    TABLE_NAME = "kijiji_vancouver_rentals"
    DB_PATH = str(Path(__file__).resolve().parents[4] / "Modules" / "engine_injesting" / "data_base" / "4260_BigData_db.db")
    CSV_PATH = "scraped_data/kijiji_rentals.csv"

    def open_spider(self, spider):
        """Called when spider starts — set up DB and CSV."""
        self.__setup_db()
        self.__setup_csv()

    def close_spider(self, spider):
        """Called when spider finishes — close connections."""
        if hasattr(self, "conn"):
            self.conn.close()
        if hasattr(self, "csv_file"):
            self.csv_file.close()
        spider.logger.info(f"Pipeline closed. Saved {self.item_count} listings.")

    def process_item(self, item, spider):
        """Process each item — clean, save to DB and CSV."""
        item = self.__clean_item(item)
        self.__save_to_db(item)
        self.__save_to_csv(item)
        self.item_count += 1
        return item

    def __setup_db(self):
        """Create DB connection and table if not exists."""
        Path(self.DB_PATH).parent.mkdir(parents=True, exist_ok=True)
        self.conn = sqlite3.connect(self.DB_PATH)
        self.conn.execute(f"""
            CREATE TABLE IF NOT EXISTS {self.TABLE_NAME} (
                listing_id      TEXT PRIMARY KEY,
                title           TEXT,
                listing_url     TEXT,
                source_website  TEXT,
                address         TEXT,
                neighbourhood   TEXT,
                city            TEXT,
                province        TEXT,
                latitude        TEXT,
                longitude       TEXT,
                price           TEXT,
                bedrooms        TEXT,
                bathrooms       TEXT,
                square_feet     TEXT,
                property_type   TEXT,
                furnished       TEXT,
                pets_allowed    TEXT,
                parking         TEXT,
                utilities_included TEXT,
                description     TEXT,
                first_seen      TEXT,
                last_seen       TEXT,
                is_active       INTEGER
            )
        """)
        self.conn.commit()
        self.item_count = 0

    def __setup_csv(self):
        """Create CSV file with headers."""
        Path(self.CSV_PATH).parent.mkdir(parents=True, exist_ok=True)
        self.csv_file = open(self.CSV_PATH, "w", newline="", encoding="utf-8")
        self.fieldnames = [
            "listing_id", "title", "listing_url", "source_website",
            "address", "neighbourhood", "city", "province",
            "latitude", "longitude", "price", "bedrooms", "bathrooms",
            "square_feet", "property_type", "furnished", "pets_allowed",
            "parking", "utilities_included", "description",
            "first_seen", "last_seen", "is_active",
        ]
        self.csv_writer = csv.DictWriter(self.csv_file, fieldnames=self.fieldnames)
        self.csv_writer.writeheader()

    def __clean_item(self, item) -> dict:
        """Clean and validate item fields."""
        cleaned = dict(item)
        for key in self.fieldnames:
            if key not in cleaned or cleaned[key] is None:
                cleaned[key] = "N/A"
        cleaned["is_active"] = 1 if cleaned.get("is_active", True) else 0
        return cleaned

    def __save_to_db(self, item: dict):
        """Insert or update listing in SQLite."""
        try:
            self.conn.execute(f"""
                INSERT OR REPLACE INTO {self.TABLE_NAME}
                (listing_id, title, listing_url, source_website,
                 address, neighbourhood, city, province,
                 latitude, longitude, price, bedrooms, bathrooms,
                 square_feet, property_type, furnished, pets_allowed,
                 parking, utilities_included, description,
                 first_seen, last_seen, is_active)
                VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)
            """, (
                item.get("listing_id"), item.get("title"), item.get("listing_url"),
                item.get("source_website"), item.get("address"), item.get("neighbourhood"),
                item.get("city"), item.get("province"), item.get("latitude"),
                item.get("longitude"), item.get("price"), item.get("bedrooms"),
                item.get("bathrooms"), item.get("square_feet"), item.get("property_type"),
                item.get("furnished"), item.get("pets_allowed"), item.get("parking"),
                item.get("utilities_included"), item.get("description"),
                item.get("first_seen"), item.get("last_seen"), item.get("is_active"),
            ))
            self.conn.commit()
        except Exception as e:
            print(f"DB error for listing {item.get('listing_id')}: {e}")

    def __save_to_csv(self, item: dict):
        """Write listing to CSV."""
        try:
            row = {k: item.get(k, "N/A") for k in self.fieldnames}
            self.csv_writer.writerow(row)
        except Exception as e:
            print(f"CSV error: {e}")
