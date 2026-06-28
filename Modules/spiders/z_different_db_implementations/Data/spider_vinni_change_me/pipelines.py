import sqlite3


class SQLitePipeline:

    def open_spider(self, spider):

        from pathlib import Path
        self.conn = sqlite3.connect((Path(__file__).resolve().parents[4] / "real_estate.db").resolve())
        self.cursor = self.conn.cursor()

        self.cursor.execute("""
        CREATE TABLE IF NOT EXISTS rew_listings (

            listing_url TEXT PRIMARY KEY,
            title TEXT,
            price INTEGER,
            monthly_rent INTEGER,
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
            features TEXT,
            facilities TEXT,
            agent_name TEXT,
            brokerage TEXT,
            property_manager TEXT,
            source_website TEXT,
            listing_type TEXT,
            first_seen TEXT,
            last_seen TEXT,
            status TEXT
        )
        """)

        self.conn.commit()

    def process_item(self, item, spider):

        self.cursor.execute("""
        INSERT OR REPLACE INTO rew_listings (
            listing_url,
            title,
            price,
            monthly_rent,
            address,
            street_address,
            neighbourhood,
            city,
            province,
            bedrooms,
            bathrooms,
            square_feet,
            lot_size,
            property_type,
            features,
            facilities,
            agent_name,
            brokerage,
            property_manager,
            source_website,
            listing_type,
            first_seen,
            last_seen,
            status
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (

             item.get("listing_url"),
            item.get("title"),
            item.get("price"),
            item.get("monthly_rent"),
            item.get("address"),
            item.get("street_address"),
            item.get("neighbourhood"),
            item.get("city"),
            item.get("province"),
            item.get("bedrooms"),
            item.get("bathrooms"),
            item.get("square_feet"),
            item.get("lot_size"),
            item.get("property_type"),
            item.get("features"),
            item.get("facilities"),
            item.get("agent_name"),
            item.get("brokerage"),
            item.get("property_manager"),
            item.get("source_website"),
            item.get("listing_type"),
            item.get("first_seen"),
            item.get("last_seen"),
            item.get("status"),
        ))

        self.conn.commit()

        return item

    def close_spider(self, spider):

        self.conn.close()