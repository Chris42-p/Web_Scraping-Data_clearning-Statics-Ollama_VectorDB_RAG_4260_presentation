import sqlite3
from pathlib import Path


class ListingSQLiteStorage:

    def __init__(self):
        #self.db_path = Path("real_estate.db")
        self.db_path = (Path(__file__).resolve().parents[4] / "real_estate.db").resolve()
        self.conn = sqlite3.connect(self.db_path)
        self.cursor = self.conn.cursor()

        self.create_table()

    def create_table(self):

        self.cursor.execute("""
        CREATE TABLE IF NOT EXISTS rew_listings (

            listing_hash TEXT PRIMARY KEY,

            title TEXT,
            price INTEGER,

            address TEXT,
            street_address TEXT,
            neighbourhood TEXT,
            city TEXT,
            province TEXT,

            bedrooms INTEGER,
            bathrooms INTEGER,

            square_feet INTEGER,

            lot_size TEXT,

            property_type TEXT,

            listing_url TEXT,

            source_website TEXT,

            first_seen TEXT,
            last_seen TEXT,

            status TEXT
        )
        """)

        self.conn.commit()

    def save(self, listings):

        for listing in listings:

            row = listing.to_json()

            self.cursor.execute("""
            INSERT OR REPLACE INTO rew_listings
            VALUES (
                ?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?
            )
            """, (

                row["listing_hash"],

                row["title"],
                row["price"],

                row["address"],
                row["street_address"],
                row["neighbourhood"],
                row["city"],
                row["province"],

                row["bedrooms"],
                row["bathrooms"],

                row["square_feet"],

                row["lot_size"],

                row["property_type"],

                row["listing_url"],

                row["source_website"],

                row["first_seen"],
                row["last_seen"],

                row["status"]
            ))

        self.conn.commit()

        print(f"Saved {len(listings)} records into SQLite.")