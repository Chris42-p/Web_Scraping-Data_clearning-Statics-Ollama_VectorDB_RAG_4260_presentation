import sqlite3


class SQLitePipeline:

    def open_spider(self, spider):

        self.conn = sqlite3.connect("real_estate.db")
        self.cursor = self.conn.cursor()

        self.cursor.execute("""
        CREATE TABLE IF NOT EXISTS rew_rentals (

            listing_url TEXT PRIMARY KEY,

            monthly_rent INTEGER,

            address TEXT,
            street_address TEXT,
            neighbourhood TEXT,
            city TEXT,
            province TEXT,

            bedrooms INTEGER,
            bathrooms INTEGER,
            square_feet INTEGER,

            property_type TEXT,
            property_manager TEXT,

            first_seen TEXT,
            last_seen TEXT,
            status TEXT
        )
        """)

        self.conn.commit()

    def process_item(self, item, spider):

        self.cursor.execute("""
        INSERT OR REPLACE INTO rew_rentals (
            listing_url,
            monthly_rent,

            address,
            street_address,
            neighbourhood,
            city,
            province,

            bedrooms,
            bathrooms,
            square_feet,

            property_type,
            property_manager,

            first_seen,
            last_seen,
            status
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (

            item.get("listing_url"),
            item.get("monthly_rent"),

            item.get("address"),
            item.get("street_address"),
            item.get("neighbourhood"),
            item.get("city"),
            item.get("province"),

            item.get("bedrooms"),
            item.get("bathrooms"),
            item.get("square_feet"),

            item.get("property_type"),
            item.get("property_manager"),

            item.get("first_seen"),
            item.get("last_seen"),
            item.get("status")
        ))

        self.conn.commit()

        return item

    def close_spider(self, spider):

        self.conn.close()