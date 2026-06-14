"""
Spider Central DB
=================
Creates and manages the central SQLite database for all spiders.
All spiders dump their Post_Data objects here.

Table structure (themed, linked by post_id):
    posts               - meta info about the post
    listings            - rental basic info
    unit_details        - physical unit details
    parsed_description  - LLM-parsed fields from Post_Description_Parser

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
                post_id         TEXT PRIMARY KEY,
                source_website  TEXT,
                post_url        TEXT,
                time_of_post    TEXT,
                time_scraped    TEXT,
                time_scraped_update TEXT,
                post_active     INTEGER DEFAULT 1
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

        conn.commit()
        conn.close()
        print(f"[SpiderCentralDB] Database ready at {self.db_path}")

    def save(self, post_data):
        """
        Save a Post_Data object into all themed tables.
        Accepts a Post_Data instance from spider_default_obj.
        """
        conn = sqlite3.connect(self.db_path)
        p = post_data
        now = datetime.utcnow().isoformat()

        try:
            # posts
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

            # listings
            conn.execute("""
                INSERT OR REPLACE INTO listings
                (post_id, user_post_title, price_of_the_unit, rent_period, city_general_area, address)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (
                str(p.post_id),
                p.user_post_title,
                p.price_of_the_unit,
                p.rent_period,
                p.city_general_area,
                p.address,
            ))

            # unit_details
            conn.execute("""
                INSERT OR REPLACE INTO unit_details
                (post_id, bed_and_bath, square_feet_unit, num_bedrooms_n_square_feet, first_pic, user_meta_tags)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (
                str(p.post_id),
                p.bed_and_bath,
                p.square_feet_unit,
                p.num_bedrooms_n_square_feet_sq,
                p.first_pic,
                str(p.user_meta_tags),
            ))

            # parsed_description (from Post_Description_Parser)
            pd = getattr(p, "_parsed", None)
            if pd:
                conn.execute("""
                    INSERT OR REPLACE INTO parsed_description
                    (post_id, smoke_free, private_room, living_situation, available_from,
                     property_type, has_ac, w_d_in_unit, furnished, wheelchair_accessible,
                     sq_footage, price_per_month, included_utilities, utility_cap,
                     close_to, travel_convenience, luxuries, llm_model_comments,
                     pets_okay, cats_okay, dogs_okay,
                     parking_included, parking_spots, parking_ev_charging, parking_details,
                     damage_deposit, other_deposits,
                     req_credit_check, req_references, req_criminal_record, req_other)
                    VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)
                """, (
                    str(p.post_id),
                    pd.smoke_free, pd.private_room, pd.living_situation, pd.living_situation,
                    pd.living_situation, pd.has_ac, pd.w_d_in_unit, pd.furnished, pd.wheelchair_accessible,
                    pd.sq_footage, pd.price_per_month, pd.included_utilities, pd.utility_cap,
                    pd.close_to, pd.travel_convenience, pd.luxuries, pd.llm_model_comments,
                    pd.pets_okay, pd.cats_okay, pd.dogs_okay,
                    pd.parking_included, pd.parking_spots, pd.parking_ev_charging, pd.parking_details,
                    pd.damage_deposit, pd.other_deposits,
                    pd.req_credit_check, pd.req_references, pd.req_criminal_record_check, pd.req_other,
                ))

            conn.commit()
            print(f"[SpiderCentralDB] Saved post_id: {p.post_id}")

        except Exception as e:
            print(f"[SpiderCentralDB] Error saving {p.post_id}: {e}")
        finally:
            conn.close()

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
    print("Tables created successfully.")
    print(f"DB location: {DB_PATH}")
