import sqlite3
from pathlib import Path
from geopy.geocoders import Nominatim
from time import sleep

class AnalysisEngine:

    def __init__(self, db_path: str = None):
        if db_path is None:
            db_path = (
                Path(__file__).resolve().parents[1]
                / "spiders"
                / "spider_default_obj"
                / "spider_central_db"
                / "listings_db.db"
            )
        self.db_path = Path(db_path).resolve()
        if not self.db_path.exists():
            raise FileNotFoundError(f"Database not found: {self.db_path}")
        
        self.conn = sqlite3.connect(str(self.db_path))
        self.conn.row_factory = sqlite3.Row
        self.cursor = self.conn.cursor()
        self._ensure_cleaned_table()

    def close(self):
        if self.conn:
            self.conn.close()
        
    #def _ensure_cleaned_table(self):
    #    self.cursor.execute("""
    #    CREATE TABLE IF NOT EXISTS rew_listings (
    #        listing_url TEXT PRIMARY KEY,
    #        title TEXT,
    #        price INTEGER,
    #        monthly_rent INTEGER,
    #        address TEXT,
    #        street_address TEXT,
    #        neighbourhood TEXT,
    #        city TEXT,
    #        province TEXT,
    #        bedrooms INTEGER,
    #        bathrooms INTEGER,
    #        square_feet INTEGER,
    #        lot_size TEXT,
    #        property_type TEXT,
    #        features TEXT,
    #        facilities TEXT,
    #        agent_name TEXT,
    #        brokerage TEXT,
    #        property_manager TEXT,
    #        source_website TEXT,
    #         listing_type TEXT,
    #        first_seen TEXT,
    #        last_seen TEXT,
    #        status TEXT
    #    )
    #    """)
    #    self.conn.commit()

    def _ensure_cleaned_table(self):
        self.cursor.execute("""
        CREATE TABLE IF NOT EXISTS cleaned_listings (
            listing_id INTEGER PRIMARY KEY,
            clean_general_area TEXT,
            clean_street_number TEXT,
            city TEXT,
            province TEXT,
            postal_code TEXT,
            address_osm TEXT,
            building_type TEXT,
            latitude REAL,
            longitude REAL,
            bounding_box TEXT,
            geocode_source TEXT,
            geocoded_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (listing_id) REFERENCES listings(id) ON DELETE CASCADE
        )
        """)
        self.conn.commit()

    

    def get_dashboard_summary(self):
        self.cursor.execute("""
            SELECT ROUND(AVG(CAST(price AS REAL)), 0) AS avg_rent
            FROM listings
            WHERE price IS NOT NULL
              AND CAST(price AS REAL) BETWEEN 500 AND 10000
        """)
        avg_row = self.cursor.fetchone()
        avg_rent = avg_row["avg_rent"] if avg_row and avg_row["avg_rent"] is not None else None

        self.cursor.execute("""
            SELECT COUNT(*) AS listing_volume
            FROM listings
        """)
        volume_row = self.cursor.fetchone()
        listing_volume = volume_row["listing_volume"] if volume_row else 0

        self.cursor.execute("""
            SELECT COUNT(*) AS new_listings
            FROM listings
            WHERE scraped_at IS NOT NULL
              AND date(scraped_at) >= date('now', '-7 day')
        """)
        new_row = self.cursor.fetchone()
        new_listings = new_row["new_listings"] if new_row else 0

        self.cursor.execute("""
            SELECT ROUND(AVG(
                CASE
                    WHEN time_on_market < 0 THEN 0
                    ELSE time_on_market
                END
            ), 0) AS days_on_market
            FROM post_status
            WHERE time_on_market IS NOT NULL
        """)
        days_row = self.cursor.fetchone()
        days_on_market = (
            int(days_row["days_on_market"])
            if days_row and days_row["days_on_market"] is not None
            else None
        )

        self.cursor.execute("""
            SELECT COUNT(*) AS updates_count
            FROM listings
            WHERE scraped_at IS NOT NULL
              AND date(scraped_at) >= date('now', '-7 day')
        """)
        updates_row = self.cursor.fetchone()
        updates_count = updates_row["updates_count"] if updates_row else 0

        return {
            "avgPrice": f"${avg_rent:,.0f}" if avg_rent is not None else "No data",
            "salesVolume": str(listing_volume or 0),
            "newListings": str(new_listings or 0),
            "daysOnMarket": str(days_on_market) if days_on_market is not None else "N/A",
            "updatesCount": int(updates_count or 0),
            "dbPath": str(self.db_path),
        }


    def get_price_trends(self):
        self.cursor.execute("""
            SELECT
                date(scraped_at) AS day,
                ROUND(AVG(CAST(price AS REAL)), 0) AS avg_price,
                COUNT(*) AS listing_count
            FROM listings
            WHERE price IS NOT NULL
              AND CAST(price AS REAL) BETWEEN 500 AND 10000
              AND scraped_at IS NOT NULL
            GROUP BY date(scraped_at)
            ORDER BY day ASC
        """)
        return [dict(row) for row in self.cursor.fetchall()]

    def get_region_distribution(self):
        self.cursor.execute("""
            SELECT
                COALESCE(NULLIF(TRIM(clean_general_area), ''), NULLIF(TRIM(general_area), ''), 'Unknown') AS region,
                COUNT(*) AS listings,
                ROUND(AVG(CAST(price AS REAL)), 0) AS avg_price
            FROM listings l
            LEFT JOIN cleaned_listings c
              ON c.listing_id = l.id
            WHERE price IS NOT NULL
              AND CAST(price AS REAL) BETWEEN 500 AND 10000
            GROUP BY COALESCE(NULLIF(TRIM(clean_general_area), ''), NULLIF(TRIM(general_area), ''), 'Unknown')
            HAVING COUNT(*) > 0
            ORDER BY listings DESC, region ASC
            LIMIT 15
        """)
        return [dict(row) for row in self.cursor.fetchall()]

    def get_map_points(self, limit: int = 250):
        self.cursor.execute("""
            SELECT
                l.id,
                l.user_post_title,
                l.price,
                l.street_number,
                l.general_area,
                l.city,
                l.province,
                l.post_url,
                c.clean_general_area,
                c.latitude,
                c.longitude,
                c.address_osm,
                c.postal_code
            FROM listings l
            INNER JOIN cleaned_listings c
                ON c.listing_id = l.id
            WHERE c.latitude IS NOT NULL
              AND c.longitude IS NOT NULL
            ORDER BY l.scraped_at DESC
            LIMIT ?
        """, (limit,))
        return [dict(row) for row in self.cursor.fetchall()]

    def get_map_listings(self, limit: int = 300):
        self.cursor.execute("""
            SELECT
                id,
                user_post_title,
                post_url,
                price,
                street_number,
                address_osm,
                '' AS clean_general_area,
                general_area,
                city,
                province,
                postal_code,
                CAST(latitude AS REAL) AS latitude,
                CAST(longitude AS REAL) AS longitude
            FROM listings
            WHERE latitude IS NOT NULL
            AND longitude IS NOT NULL
            AND CAST(latitude AS REAL) BETWEEN 49.0 AND 49.5
            AND CAST(longitude AS REAL) BETWEEN -123.4 AND -122.9
            ORDER BY scraped_at DESC
            LIMIT ?
        """, (limit,))
        return [dict(row) for row in self.cursor.fetchall()]

    
    def backfill_missing_coordinates(self, limit: int = 200):
        geolocator = Nominatim(user_agent="housing_dashboard_geocoder")

        self.cursor.execute("""
            SELECT
                l.id,
                l.general_area,
                l.street_number,
                l.city,
                l.province,
                l.postal_code,
                c.clean_general_area,
                c.clean_street_number
            FROM listings l
            LEFT JOIN cleaned_listings c
                ON c.listing_id = l.id
            WHERE (
                c.latitude IS NULL
                OR c.longitude IS NULL
            )
            AND COALESCE(NULLIF(TRIM(c.clean_street_number), ''), NULLIF(TRIM(l.street_number), '')) IS NOT NULL
            LIMIT ?
        """, (limit,))
        rows = self.cursor.fetchall()

        updated = 0

        for row in rows:
            listing_id = row["id"]

            street = row["clean_street_number"] or row["street_number"]
            city = row["city"] or "Vancouver"
            province = row["province"] or "BC"
            postal_code = row["postal_code"] or ""
            clean_area = row["clean_general_area"] or row["general_area"] or ""

            address_parts = [street, clean_area, city, province, postal_code, "Canada"]
            query = ", ".join(part for part in address_parts if part)

            try:
                location = geolocator.geocode(query, timeout=10)
                if not location:
                    continue

                self.cursor.execute("""
                    INSERT INTO cleaned_listings (
                        listing_id,
                        clean_general_area,
                        clean_street_number,
                        city,
                        province,
                        postal_code,
                        address_osm,
                        latitude,
                        longitude,
                        geocode_source,
                        geocoded_at,
                        updated_at
                    )
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP)
                    ON CONFLICT(listing_id) DO UPDATE SET
                        clean_general_area = COALESCE(excluded.clean_general_area, cleaned_listings.clean_general_area),
                        clean_street_number = COALESCE(excluded.clean_street_number, cleaned_listings.clean_street_number),
                        city = COALESCE(excluded.city, cleaned_listings.city),
                        province = COALESCE(excluded.province, cleaned_listings.province),
                        postal_code = COALESCE(excluded.postal_code, cleaned_listings.postal_code),
                        address_osm = COALESCE(excluded.address_osm, cleaned_listings.address_osm),
                        latitude = excluded.latitude,
                        longitude = excluded.longitude,
                        geocode_source = excluded.geocode_source,
                        updated_at = CURRENT_TIMESTAMP
                """, (
                    listing_id,
                    clean_area,
                    street,
                    city,
                    province,
                    postal_code,
                    location.address,
                    float(location.latitude),
                    float(location.longitude),
                    "nominatim",
                ))

                updated += 1
                sleep(1)

            except Exception as exc:
                print(f"geocode failed for id={listing_id}: {exc}")

        self.conn.commit()
        return {"updated": updated, "attempted": len(rows)}