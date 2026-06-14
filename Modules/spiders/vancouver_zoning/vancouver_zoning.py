"""
4.2.2.1 - City Spider: Vancouver Zoning Data
Source: City of Vancouver Open Data Portal
API: OpenDataSoft v2.1
Dataset: zoning-districts-and-labels
Updated: weekly
"""

import requests
import json
import sqlite3
import os
import logging
from datetime import datetime

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)

BASE_URL = "https://opendata.vancouver.ca/api/explore/v2.1/catalog/datasets"
DATASET_ID = "zoning-districts-and-labels"
BATCH_SIZE = 100


class VancouverZoningClient:
    """
    Fetches zoning district data from the City of Vancouver Open Data API.
    Stores results in SQLite via spider_central_db for use by the analytics engine (Step 4).
    Corresponds to flow diagram node: 4.2.2.1 City spider - zoning area
    """

    def __init__(self, db_path: str = None):
        if db_path is None:
            base_dir = os.path.dirname(os.path.abspath(__file__))
            db_path = os.path.join(base_dir, "..", "spider_central_db", "vancouver_zoning.db")
        self.db_path = db_path
        self._init_db()

    def _init_db(self):
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
        conn = sqlite3.connect(self.db_path)
        conn.execute("""
            CREATE TABLE IF NOT EXISTS zoning_districts (
                id              INTEGER PRIMARY KEY AUTOINCREMENT,
                zone_name       TEXT,
                zone_category   TEXT,
                geo_json        TEXT,
                fetched_at      TEXT
            )
        """)
        conn.commit()
        conn.close()
        logger.info(f"Database ready at {self.db_path}")

    def fetch_all(self) -> list[dict]:
        """
        Pages through the entire zoning dataset and returns all records.
        """
        records = []
        offset = 0

        while True:
            url = f"{BASE_URL}/{DATASET_ID}/records"
            params = {
                "limit": BATCH_SIZE,
                "offset": offset,
            }

            try:
                response = requests.get(url, params=params, timeout=30)
                response.raise_for_status()
                data = response.json()
            except requests.RequestException as e:
                logger.error(f"Request failed at offset {offset}: {e}")
                break

            batch = data.get("results", [])
            if not batch:
                break

            records.extend(batch)
            logger.info(f"Fetched {len(records)} records so far...")
            offset += BATCH_SIZE

            if len(batch) < BATCH_SIZE:
                break

        logger.info(f"Total records fetched: {len(records)}")
        return records

    def save_to_db(self, records: list[dict]):
        """
        Saves fetched zoning records into SQLite.
        Clears old data first to stay in sync with the weekly API update cycle.
        """
        conn = sqlite3.connect(self.db_path)
        conn.execute("DELETE FROM zoning_districts")

        fetched_at = datetime.utcnow().isoformat()

        rows = []
        for r in records:
            fields = r.get("fields", r)
            zone_name     = fields.get("zone_name") or fields.get("zonename") or fields.get("label") or ""
            zone_category = fields.get("zone_category") or fields.get("zonecategory") or fields.get("category") or ""
            geo           = r.get("geo_shape") or r.get("geometry") or {}
            rows.append((zone_name, zone_category, json.dumps(geo), fetched_at))

        conn.executemany(
            "INSERT INTO zoning_districts (zone_name, zone_category, geo_json, fetched_at) VALUES (?, ?, ?, ?)",
            rows
        )
        conn.commit()
        conn.close()
        logger.info(f"Saved {len(rows)} zoning records to database.")

    def run(self):
        """
        Main entry point: fetch and save all zoning data.
        Call this from spider_central_db or main.py scheduler.
        """
        logger.info("Starting Vancouver Zoning data fetch...")
        records = self.fetch_all()
        if records:
            self.save_to_db(records)
            logger.info("Done.")
        else:
            logger.warning("No records returned from API.")


if __name__ == "__main__":
    client = VancouverZoningClient()
    client.run()
