"""
Sync Geographic Data to Spider Central DB
==========================================
Reads data from individual spider DBs and writes into spider_central.db

Sources:
    - vancouver_zoning.db     → zoning_districts table
    - safety_convenience.db   → transit_stations, parks, schools, crime_incidents tables

Usage:
    cd Modules/spiders
    python sync_to_central.py

Run this after running:
    - vancouver_zoning spider
    - safety_convenience_spider
"""

import sqlite3
import os
import sys

# ── Paths ─────────────────────────────────────────────────────────────
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

ZONING_DB = os.path.join(BASE_DIR, "spider_central_db", "vancouver_zoning.db")
SAFETY_DB = os.path.join(BASE_DIR, "spider_central_db", "safety_convenience.db")

# Spider central DB via SpiderCentralDB class
sys.path.insert(0, os.path.join(BASE_DIR, "spider_default_obj", "spider_central_db"))
from spider_default_db import SpiderCentralDB


def sync_zoning(db: SpiderCentralDB):
    """Read zoning_districts from vancouver_zoning.db → spider_central.db"""
    if not os.path.exists(ZONING_DB):
        print(f"[sync] Zoning DB not found: {ZONING_DB}")
        return

    conn = sqlite3.connect(ZONING_DB)
    conn.row_factory = sqlite3.Row
    rows = conn.execute("SELECT * FROM zoning_districts").fetchall()
    conn.close()

    records = [dict(r) for r in rows]
    db.save_zoning(records)
    print(f"[sync] Zoning: {len(records)} records synced.")


def sync_transit(db: SpiderCentralDB):
    """Read transit_stations from safety_convenience.db → spider_central.db"""
    if not os.path.exists(SAFETY_DB):
        print(f"[sync] Safety DB not found: {SAFETY_DB}")
        return

    conn = sqlite3.connect(SAFETY_DB)
    conn.row_factory = sqlite3.Row
    rows = conn.execute("SELECT * FROM transit_stations").fetchall()
    conn.close()

    records = [dict(r) for r in rows]
    db.save_transit(records)
    print(f"[sync] Transit: {len(records)} records synced.")


def sync_parks(db: SpiderCentralDB):
    """Read parks from safety_convenience.db → spider_central.db"""
    conn = sqlite3.connect(SAFETY_DB)
    conn.row_factory = sqlite3.Row
    rows = conn.execute("SELECT * FROM parks").fetchall()
    conn.close()

    records = [dict(r) for r in rows]
    db.save_parks(records)
    print(f"[sync] Parks: {len(records)} records synced.")


def sync_schools(db: SpiderCentralDB):
    """Read schools from safety_convenience.db → spider_central.db"""
    conn = sqlite3.connect(SAFETY_DB)
    conn.row_factory = sqlite3.Row
    rows = conn.execute("SELECT * FROM schools").fetchall()
    conn.close()

    records = [dict(r) for r in rows]
    db.save_schools(records)
    print(f"[sync] Schools: {len(records)} records synced.")


def sync_crime(db: SpiderCentralDB):
    """Read crime_incidents from safety_convenience.db → spider_central.db"""
    conn = sqlite3.connect(SAFETY_DB)
    conn.row_factory = sqlite3.Row
    rows = conn.execute("SELECT * FROM crime_incidents").fetchall()
    conn.close()

    records = [dict(r) for r in rows]
    db.save_crime(records)
    print(f"[sync] Crime: {len(records)} records synced.")


def run_all():
    print("=== Syncing geographic data to spider_central.db ===")
    db = SpiderCentralDB()

    sync_zoning(db)
    sync_transit(db)
    sync_parks(db)
    sync_schools(db)
    sync_crime(db)

    print("=== Sync complete ===")


if __name__ == "__main__":
    run_all()
