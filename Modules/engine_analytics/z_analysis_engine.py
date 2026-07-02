import sqlite3
from pathlib import Path


class AnalysisEngine:

    def __init__(self, db_path: str = None):
        if db_path is None:
            db_path = Path(__file__).resolve().parents[1] / "spiders" / "z_not_spiders" / "spider_central.db"
        self.db_path = Path(db_path).resolve()
        if not self.db_path.exists():
            raise FileNotFoundError(f"Database not found: {self.db_path}")
        db_uri = f"file:{self.db_path.as_posix()}?mode=rw"
        self.conn = sqlite3.connect(db_uri, uri=True)
        self.conn.row_factory = sqlite3.Row
        self.cursor = self.conn.cursor()
        self._ensure_rew_table()

    def close(self):
        if self.conn:
            self.conn.close()
        
    def _ensure_rew_table(self):
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

    def average_price_by_neighbourhood(self):

        self.cursor.execute("""
            SELECT
                neighbourhood,
                ROUND(AVG(price), 0) AS avg_price,
                COUNT(*) AS listings
            FROM rew_listings
            WHERE price IS NOT NULL
            GROUP BY neighbourhood
            ORDER BY avg_price DESC
        """)

        rows = self.cursor.fetchall()

        print("\n=== Average Price By Neighbourhood ===\n")

        for row in rows:
            neighbourhood, avg_price, listings = row

            print(
                f"{neighbourhood:<25}"
                f"${avg_price:,.0f}   "
                f"({listings} listings)"
            )

    def average_price_per_sqft(self):

        self.cursor.execute("""
            SELECT
                neighbourhood,
                ROUND(AVG(price * 1.0 / square_feet),2)
            FROM rew_listings
            WHERE
                price IS NOT NULL
                AND square_feet IS NOT NULL
                AND square_feet > 0
            GROUP BY neighbourhood
            ORDER BY AVG(price * 1.0 / square_feet) DESC
        """)

        rows = self.cursor.fetchall()

        print("\n=== Average Price Per SqFt ===\n")

        for row in rows:
            print(row)

    def get_dashboard_summary(self):
        self.cursor.execute("""
            SELECT ROUND(AVG(price), 0)
            FROM rew_listings
            WHERE price IS NOT NULL
        """)
        avg_price_row = self.cursor.fetchone()
        avg_price = avg_price_row[0] if avg_price_row else None

        self.cursor.execute("""
            SELECT COUNT(*)
            FROM rew_listings
        """)
        sales_volume_row = self.cursor.fetchone()
        sales_volume = sales_volume_row[0] if sales_volume_row else 0

        self.cursor.execute("""
            SELECT COUNT(*)
            FROM rew_listings
            WHERE first_seen IS NOT NULL
        """)
        new_listings_row = self.cursor.fetchone()
        new_listings = new_listings_row[0] if new_listings_row else 0

        self.cursor.execute("""
            SELECT ROUND(AVG(julianday('now') - julianday(first_seen)), 0)
            FROM rew_listings
            WHERE first_seen IS NOT NULL
              AND status IS NOT NULL
              AND LOWER(status) = 'active'
        """)
        days_on_market_row = self.cursor.fetchone()
        days_on_market = int(days_on_market_row[0]) if days_on_market_row and days_on_market_row[0] is not None else None

        self.cursor.execute("""
            SELECT COUNT(*)
            FROM rew_listings
            WHERE last_seen IS NOT NULL
            AND date(last_seen) >= date('now', '-7 day')
        """)
        updates_count_row = self.cursor.fetchone()
        updates_count = updates_count_row[0] if updates_count_row else 0

        self.cursor.execute("""
            SELECT COUNT(*)
            FROM rew_listings
            WHERE status IS NOT NULL
            AND LOWER(status) = 'active'
        """)
        active_listings_row = self.cursor.fetchone()
        active_listings = active_listings_row[0] if active_listings_row else 0

        return {
            "avgPrice": f"${avg_price:,.0f}" if avg_price is not None else "No data",
            "salesVolume": str(sales_volume or 0),
            "newListings": str(new_listings or 0),
            "daysOnMarket": str(days_on_market) if days_on_market is not None else "N/A",
            "updatesCount": int(updates_count or 0),
            "activeListings": str(active_listings or 0),
            "dbPath": str(self.db_path),
        }


    def property_type_distribution(self):

        self.cursor.execute("""
            SELECT
                property_type,
                COUNT(*)
            FROM rew_listings
            GROUP BY property_type
            ORDER BY COUNT(*) DESC
        """)

        rows = self.cursor.fetchall()

        print("\n=== Property Type Distribution ===\n")

        for row in rows:
            print(row)

    
    def average_rooms_by_neighbourhood(self):

        self.cursor.execute("""
            SELECT
                neighbourhood,
                ROUND(AVG(bedrooms), 1) AS avg_bedrooms,
                ROUND(AVG(bathrooms), 1) AS avg_bathrooms,
                COUNT(*) AS listings
            FROM rew_listings
            WHERE bedrooms IS NOT NULL
            GROUP BY neighbourhood
            ORDER BY avg_bedrooms DESC
        """)

        rows = self.cursor.fetchall()

        print("\n=== Average Bedrooms/Bathrooms By Neighbourhood ===\n")

        for row in rows:
            neighbourhood, avg_bedrooms, avg_bathrooms, listings = row

            print(
                f"{neighbourhood:<25}"
                f"Beds: {avg_bedrooms:<4} "
                f"Baths: {avg_bathrooms:<4} "
                f"({listings} listings)"
            )

    def top_5_most_expensive(self):

        self.cursor.execute("""
            SELECT
                price,
                address,
                property_type,
                bedrooms,
                bathrooms,
                square_feet
            FROM rew_listings
            WHERE price IS NOT NULL
            ORDER BY price DESC
            LIMIT 5
        """)

        rows = self.cursor.fetchall()

        print("\n=== Top 5 Most Expensive Listings ===\n")

        for row in rows:
            price, address, property_type, bedrooms, bathrooms, square_feet = row

            print(
                f"${price:,.0f} | "
                f"{address} | "
                f"{property_type} | "
                f"{bedrooms} bd / {bathrooms} ba | "
                f"{square_feet} sqft"
            )

    def run(self):

        try:

            self.average_price_by_neighbourhood()

            self.average_price_per_sqft()

            self.property_type_distribution()

            self.average_rooms_by_neighbourhood()

            self.top_5_most_expensive()
        finally:
            self.close()


if __name__ == "__main__":
    AnalysisEngine().run()