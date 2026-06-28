"""
Spider Central DB
=================
Creates and manages the central SQLite database for all spiders.
All spiders dump their Post_Data objects here.

Table structure:
    -- Rental listings (from Post_Data) --
    posts               - meta info about the post
    listings            - rental basic info
    unit_details        - physical unit details
    parsed_description  - LLM-parsed fields from Post_Description_Parser

    -- Geographic data (from vancouver_zoning + safety_convenience spiders) --
    zoning_districts    - Vancouver zoning areas (4.2.2.1)
    transit_stations    - Skytrain stations (4.2.2.3)
    parks               - Vancouver parks with coordinates (4.2.2.3)
    schools             - Vancouver schools (4.2.2.3)
    crime_incidents     - VPD crime data 2020-2025 (4.2.2.3)

Usage:
    from spider_central_db.spider_default_db import SpiderCentralDB
    db = SpiderCentralDB()
    db.save(post_data_obj)
"""

import sqlite3
import os
from datetime import datetime


DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "spider_central.db")


class SpiderCentralDB:

    def __init__(self, db_path: str = None):
        self.db_path = db_path or DB_PATH
        self._init_db()

    def _init_db(self):
        conn = sqlite3.connect(self.db_path)

        # ── Table 1: posts (meta) ──────────────────────────────────────
        conn.execute("""
            CREATE TABLE IF NOT EXISTS posts (
                post_id             TEXT PRIMARY KEY,
                source_website      TEXT,
                post_url            TEXT,
                time_of_post        TEXT,
                time_scraped        TEXT,
                time_scraped_update TEXT,
                post_active         INTEGER DEFAULT 1
            )
        """)

        # ── Table 2: listings (rental basics) ─────────────────────────
        conn.execute("""
            CREATE TABLE IF NOT EXISTS listings (
                post_id             TEXT PRIMARY KEY,
                user_post_title     TEXT,
                price_of_the_unit   TEXT,
                rent_period         TEXT,
                city_general_area   TEXT,
                address             TEXT,
                street_number       TEXT,
                city                TEXT,
                province            TEXT,
                postal_code         TEXT,
                FOREIGN KEY (post_id) REFERENCES posts(post_id)
            )
        """)

        # ── Table 3: unit_details (physical unit info) ─────────────────
        conn.execute("""
            CREATE TABLE IF NOT EXISTS unit_details (
                post_id                     TEXT PRIMARY KEY,
                bed_and_bath                TEXT,
                square_feet_unit            TEXT,
                num_bedrooms_n_square_feet  TEXT,
                first_pic                   TEXT,
                user_meta_tags              TEXT,
                FOREIGN KEY (post_id) REFERENCES posts(post_id)
            )
        """)

        # ── Table 4: parsed_description (LLM output) ──────────────────
        conn.execute("""
            CREATE TABLE IF NOT EXISTS parsed_description (
                post_id                 TEXT PRIMARY KEY,
                smoke_free              INTEGER,
                private_room            INTEGER,
                living_situation        TEXT,
                available_from          TEXT,
                property_type           TEXT,
                has_ac                  INTEGER,
                w_d_in_unit             INTEGER,
                furnished               INTEGER,
                wheelchair_accessible   INTEGER,
                sq_footage              INTEGER,
                price_per_month         INTEGER,
                included_utilities      TEXT,
                utility_cap             TEXT,
                close_to                TEXT,
                travel_convenience      TEXT,
                luxuries                TEXT,
                llm_model_comments      TEXT,
                pets_okay               INTEGER,
                cats_okay               INTEGER,
                dogs_okay               INTEGER,
                parking_included        INTEGER,
                parking_spots           INTEGER,
                parking_ev_charging     INTEGER,
                parking_details         TEXT,
                damage_deposit          TEXT,
                other_deposits          TEXT,
                req_credit_check        INTEGER,
                req_references          INTEGER,
                req_criminal_record     INTEGER,
                req_other               TEXT,
                FOREIGN KEY (post_id) REFERENCES posts(post_id)
            )
        """)

        # ── Table 5: zoning_districts (4.2.2.1) ───────────────────────
        conn.execute("""
            CREATE TABLE IF NOT EXISTS zoning_districts (
                id              INTEGER PRIMARY KEY AUTOINCREMENT,
                zone_name       TEXT,
                zone_category   TEXT,
                geo_json        TEXT,
                fetched_at      TEXT
            )
        """)

        # ── Table 6: transit_stations (4.2.2.3) ───────────────────────
        conn.execute("""
            CREATE TABLE IF NOT EXISTS transit_stations (
                id          INTEGER PRIMARY KEY AUTOINCREMENT,
                name        TEXT,
                line        TEXT,
                latitude    REAL,
                longitude   REAL,
                fetched_at  TEXT
            )
        """)

        # ── Table 7: parks (4.2.2.3) ──────────────────────────────────
        conn.execute("""
            CREATE TABLE IF NOT EXISTS parks (
                id              INTEGER PRIMARY KEY AUTOINCREMENT,
                name            TEXT,
                neighbourhood   TEXT,
                facilities      TEXT,
                latitude        REAL,
                longitude       REAL,
                fetched_at      TEXT
            )
        """)

        # ── Table 8: schools (4.2.2.3) ────────────────────────────────
        conn.execute("""
            CREATE TABLE IF NOT EXISTS schools (
                id          INTEGER PRIMARY KEY AUTOINCREMENT,
                name        TEXT,
                category    TEXT,
                address     TEXT,
                latitude    REAL,
                longitude   REAL,
                fetched_at  TEXT
            )
        """)

        # ── Table 9: crime_incidents (4.2.2.3) ────────────────────────
        conn.execute("""
            CREATE TABLE IF NOT EXISTS crime_incidents (
                id              INTEGER PRIMARY KEY AUTOINCREMENT,
                year            INTEGER,
                month           INTEGER,
                day             INTEGER,
                hour            INTEGER,
                minute          INTEGER,
                offence_type    TEXT,
                neighbourhood   TEXT,
                hundred_block   TEXT,
                latitude        REAL,
                longitude       REAL,
                fetched_at      TEXT
            )
        """)

        conn.commit()
        conn.close()
        print(f"[SpiderCentralDB] Database ready at {self.db_path}")

    # ── Rental listing save ────────────────────────────────────────────

    def save(self, post_data):
        """
        Save a Post_Data object into all rental themed tables.
        """
        conn = sqlite3.connect(self.db_path)
        p = post_data
        now = datetime.utcnow().isoformat()

        try:
            conn.execute("""
                INSERT OR REPLACE INTO posts
                (post_id, source_website, post_url, time_of_post, time_scraped, post_active)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (
                str(p.post_id),
                getattr(p, "source_website", "unknown"),
                p.post_url,
                p.time_of_post,
                p.time_scraped or now,
                1,
            ))

            conn.execute("""
                INSERT OR REPLACE INTO listings
                (post_id, user_post_title, price_of_the_unit, rent_period,
                 city_general_area, address, street_number, city, province, postal_code)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                str(p.post_id),
                p.user_post_title,
                p.price_of_the_unit,
                p.rent_period,
                getattr(p, "general_area", "N/A"),
                p.address if hasattr(p, "address") else getattr(p, "street_number", "N/A"),
                getattr(p, "street_number", "N/A"),
                getattr(p, "city", "N/A"),
                getattr(p, "province", "N/A"),
                getattr(p, "postal_code", "N/A"),
            ))

            conn.execute("""
                INSERT OR REPLACE INTO unit_details
                (post_id, bed_and_bath, square_feet_unit, num_bedrooms_n_square_feet,
                 first_pic, user_meta_tags)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (
                str(p.post_id),
                getattr(p, "bed_bath", "N/A"),
                p.square_feet_unit,
                getattr(p, "sqr_feet", "N/A"),
                p.first_pic,
                str(p.user_meta_tags),
            ))

            conn.commit()
            print(f"[SpiderCentralDB] Saved post_id: {p.post_id}")

        except Exception as e:
            print(f"[SpiderCentralDB] Error saving {p.post_id}: {e}")
        finally:
            conn.close()

    # ── Geographic data save ───────────────────────────────────────────

    def save_zoning(self, records: list[dict]):
        """Save zoning records from vancouver_zoning spider."""
        conn = sqlite3.connect(self.db_path)
        conn.execute("DELETE FROM zoning_districts")
        fetched_at = datetime.utcnow().isoformat()
        rows = [(r.get("zone_name",""), r.get("zone_category",""),
                 r.get("geo_json",""), fetched_at) for r in records]
        conn.executemany(
            "INSERT INTO zoning_districts (zone_name, zone_category, geo_json, fetched_at) VALUES (?,?,?,?)",
            rows
        )
        conn.commit()
        conn.close()
        print(f"[SpiderCentralDB] Saved {len(rows)} zoning records.")

    def save_transit(self, records: list[dict]):
        """Save transit station records from safety_convenience spider."""
        conn = sqlite3.connect(self.db_path)
        conn.execute("DELETE FROM transit_stations")
        fetched_at = datetime.utcnow().isoformat()
        rows = [(r.get("name",""), r.get("line",""),
                 r.get("latitude"), r.get("longitude"), fetched_at) for r in records]
        conn.executemany(
            "INSERT INTO transit_stations (name, line, latitude, longitude, fetched_at) VALUES (?,?,?,?,?)",
            rows
        )
        conn.commit()
        conn.close()
        print(f"[SpiderCentralDB] Saved {len(rows)} transit stations.")

    def save_parks(self, records: list[dict]):
        """Save parks records from safety_convenience spider."""
        conn = sqlite3.connect(self.db_path)
        conn.execute("DELETE FROM parks")
        fetched_at = datetime.utcnow().isoformat()
        rows = [(r.get("name",""), r.get("neighbourhood",""), r.get("facilities",""),
                 r.get("latitude"), r.get("longitude"), fetched_at) for r in records]
        conn.executemany(
            "INSERT INTO parks (name, neighbourhood, facilities, latitude, longitude, fetched_at) VALUES (?,?,?,?,?,?)",
            rows
        )
        conn.commit()
        conn.close()
        print(f"[SpiderCentralDB] Saved {len(rows)} parks.")

    def save_schools(self, records: list[dict]):
        """Save schools records from safety_convenience spider."""
        conn = sqlite3.connect(self.db_path)
        conn.execute("DELETE FROM schools")
        fetched_at = datetime.utcnow().isoformat()
        rows = [(r.get("name",""), r.get("category",""), r.get("address",""),
                 r.get("latitude"), r.get("longitude"), fetched_at) for r in records]
        conn.executemany(
            "INSERT INTO schools (name, category, address, latitude, longitude, fetched_at) VALUES (?,?,?,?,?,?)",
            rows
        )
        conn.commit()
        conn.close()
        print(f"[SpiderCentralDB] Saved {len(rows)} schools.")

    def save_crime(self, records: list[dict]):
        """Save VPD crime records from safety_convenience spider."""
        conn = sqlite3.connect(self.db_path)
        conn.execute("DELETE FROM crime_incidents")
        fetched_at = datetime.utcnow().isoformat()
        rows = [(
            r.get("year"), r.get("month"), r.get("day"),
            r.get("hour"), r.get("minute"),
            r.get("offence_type",""), r.get("neighbourhood",""),
            r.get("hundred_block",""),
            r.get("latitude"), r.get("longitude"), fetched_at
        ) for r in records]
        conn.executemany("""
            INSERT INTO crime_incidents
            (year, month, day, hour, minute, offence_type, neighbourhood,
             hundred_block, latitude, longitude, fetched_at)
            VALUES (?,?,?,?,?,?,?,?,?,?,?)
        """, rows)
        conn.commit()
        conn.close()
        print(f"[SpiderCentralDB] Saved {len(rows)} crime incidents.")

    # ── Query helpers ──────────────────────────────────────────────────

    def get_all_posts(self) -> list:
        """Return all posts joined with listing info."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.execute("""
            SELECT p.post_id, p.source_website, p.time_scraped,
                   l.user_post_title, l.price_of_the_unit, l.address
            FROM posts p
            LEFT JOIN listings l ON p.post_id = l.post_id
            ORDER BY p.time_scraped DESC
        """)
        rows = cursor.fetchall()
        conn.close()
        return rows


if __name__ == "__main__":
    db = SpiderCentralDB()
    print("All tables created successfully.")
    print(f"DB location: {DB_PATH}")
