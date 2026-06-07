import sqlite3
from pathlib import Path


class ListingSQLiteStorage:

    def __init__(self):
        self.db_path = Path("real_estate.db")
        self.conn = sqlite3.connect(self.db_path)
        self.cursor = self.conn.cursor()

        self.create_table()

    def create_table(self):

        self.cursor.execute("""
        CREATE TABLE IF NOT EXISTS rew_listings (

    listing_hash TEXT PRIMARY KEY,

    title TEXT,
    listing_url TEXT,
    source_website TEXT,

    img_of_unit TEXT,

    days_ago_posted TEXT,
    post_updated TEXT,

    first_seen TEXT,
    last_seen TEXT,
    status TEXT,

    address TEXT,
    street_address TEXT,
    neighbourhood TEXT,
    city TEXT,
    province TEXT,

    postal_code TEXT,
    latitude TEXT,
    longitude TEXT,

    price INTEGER,
    bedrooms INTEGER,
    bathrooms INTEGER,
    square_feet INTEGER,

    lot_size TEXT,
    property_type TEXT,

    post_description TEXT,

    amenities TEXT,
    features TEXT,
    facilities TEXT,

    parking TEXT,
    smoking TEXT,

    agent_name TEXT,
    brokerage TEXT,

    mls_number TEXT,

    building_name TEXT,
    building_age TEXT,
    year_built TEXT
)
        """)

        self.conn.commit()

    def save(self, listings):

        for listing in listings:

            row = listing.to_json()

            self.cursor.execute("""
            INSERT OR REPLACE INTO rew_listings (
    listing_hash,
    title,
    listing_url,
    source_website,
    img_of_unit,
    days_ago_posted,
    post_updated,
    first_seen,
    last_seen,
    status,
    address,
    street_address,
    neighbourhood,
    city,
    province,
    postal_code,
    latitude,
    longitude,
    price,
    bedrooms,
    bathrooms,
    square_feet,
    lot_size,
    property_type,
    post_description,
    amenities,
    features,
    facilities,
    parking,
    smoking,
    agent_name,
    brokerage,
    mls_number,
    building_name,
    building_age,
    year_built
)
VALUES (
    ?,?,?,?,?,?,?,?,?,?,
    ?,?,?,?,?,?,?,?,?,?,
    ?,?,?,?,?,?,?,?,?,?,
    ?,?,?,?,?,?
)
            """, (

                row["listing_hash"],
                row["title"],
                row["listing_url"],
                row["source_website"],
                row["img_of_unit"],
                row["days_ago_posted"],
                row["post_updated"],
                row["first_seen"],
                row["last_seen"],
                row["status"],
                row["address"],
                row["street_address"],
                row["neighbourhood"],
                row["city"],
                row["province"],
                row["postal_code"],
                row["latitude"],
                row["longitude"],
                row["price"],
                row["bedrooms"],
                row["bathrooms"],
                row["square_feet"],
                row["lot_size"],
                row["property_type"],
                row["post_description"],
                row["amenities"],
                row["features"],
                row["facilities"],
                row["parking"],
                row["smoking"],
                row["agent_name"],
                row["brokerage"],
                row["mls_number"],
                row["building_name"],
                row["building_age"],
row["year_built"],
            ))

        self.conn.commit()

        print(f"Saved {len(listings)} records into SQLite.")