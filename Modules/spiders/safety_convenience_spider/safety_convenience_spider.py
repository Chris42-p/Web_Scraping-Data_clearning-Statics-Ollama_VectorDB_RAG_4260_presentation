"""
4.2.2.3 - City Spider: Safety & Convenience Data
Sources:
  - City of Vancouver Open Data API (OpenDataSoft v2.1):
      rapid-transit-stations, parks, schools
  - VPD GeoDASH (CSV download):
      crime data by year and neighbourhood

Stores all results in SQLite via spider_central_db.
"""
import csv
import requests
import sqlite3
import json
import os
import logging
import io
import zipfile


from datetime import datetime

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)

BASE_URL = "https://opendata.vancouver.ca/api/explore/v2.1/catalog/datasets"
BATCH_SIZE = 100

# VPD crime CSV download URL pattern
# year: 2003-2026, neighbourhood: e.g. "Kitsilano" or use "ALL" for all
VPD_CSV_URL = "https://geodash.vpd.ca/opendata/crimedata_download/crimedata_csv_AllNeighbourhoods_{year}.zip"


class SafetyConvenienceSpider:
    """
    Fetches safety and convenience data for Vancouver neighbourhoods.
    Corresponds to flow diagram node: 4.2.2.3
    """

    def __init__(self, db_path: str = None):
        if db_path is None:
            base_dir = os.path.dirname(os.path.abspath(__file__))
            db_path = os.path.join(base_dir, "..", "spider_central_db", "safety_convenience.db")
        self.db_path = db_path
        self._init_db()

    def _init_db(self):
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
        conn = sqlite3.connect(self.db_path)

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

        conn.execute("""
            CREATE TABLE IF NOT EXISTS parks (
                id          INTEGER PRIMARY KEY AUTOINCREMENT,
                name        TEXT,
                neighbourhood TEXT,
                facilities  TEXT,
                latitude    REAL,
                longitude   REAL,
                fetched_at  TEXT
            )
        """)

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
        logger.info(f"Database ready at {self.db_path}")

    # ------------------------------------------------------------------ #
    #  Vancouver Open Data API helpers
    # ------------------------------------------------------------------ #

    def _fetch_dataset(self, dataset_id: str) -> list[dict]:
        """Generic paginated fetcher for Vancouver Open Data API."""
        records = []
        offset = 0
        while True:
            url = f"{BASE_URL}/{dataset_id}/records"
            params = {"limit": BATCH_SIZE, "offset": offset}
            try:
                r = requests.get(url, params=params, timeout=30)
                r.raise_for_status()
                data = r.json()
            except requests.RequestException as e:
                logger.error(f"[{dataset_id}] Request failed at offset {offset}: {e}")
                break
            batch = data.get("results", [])
            if not batch:
                break
            records.extend(batch)
            offset += BATCH_SIZE
            if len(batch) < BATCH_SIZE:
                break
        logger.info(f"[{dataset_id}] Total records: {len(records)}")
        return records

    def _get_geo(self, record: dict):
        """Extract lat/lon from a record's geo_point_2d field."""
        geo = record.get("geo_point_2d") or {}
        return geo.get("lat"), geo.get("lon")

    # ------------------------------------------------------------------ #
    #  Transit stations
    # ------------------------------------------------------------------ #

    def fetch_transit_stations(self):
        records = self._fetch_dataset("rapid-transit-stations")
        fetched_at = datetime.utcnow().isoformat()
        rows = []
        for r in records:
            lat, lon = self._get_geo(r)
            rows.append((
                r.get("station") or r.get("name") or "",
                r.get("line") or r.get("transit_line") or "",
                lat, lon, fetched_at
            ))
        conn = sqlite3.connect(self.db_path)
        conn.execute("DELETE FROM transit_stations")
        conn.executemany(
            "INSERT INTO transit_stations (name, line, latitude, longitude, fetched_at) VALUES (?,?,?,?,?)",
            rows
        )
        conn.commit()
        conn.close()
        logger.info(f"Saved {len(rows)} transit stations.")

    # ------------------------------------------------------------------ #
    #  Parks
    # ------------------------------------------------------------------ #

    def fetch_parks(self):
        records = self._fetch_dataset("parks")
        fetched_at = datetime.utcnow().isoformat()
        rows = []
        for r in records:
            lat, lon = self._get_geo(r)
            rows.append((
                r.get("name") or r.get("parkname") or "",
                r.get("neighbourhood_name") or r.get("neighbourhood") or "",
                json.dumps(r.get("facilities", [])),
                lat, lon, fetched_at
            ))
        conn = sqlite3.connect(self.db_path)
        conn.execute("DELETE FROM parks")
        conn.executemany(
            "INSERT INTO parks (name, neighbourhood, facilities, latitude, longitude, fetched_at) VALUES (?,?,?,?,?,?)",
            rows
        )
        conn.commit()
        conn.close()
        logger.info(f"Saved {len(rows)} parks.")

    # ------------------------------------------------------------------ #
    #  Schools
    # ------------------------------------------------------------------ #

    def fetch_schools(self):
        records = self._fetch_dataset("schools")
        fetched_at = datetime.utcnow().isoformat()
        rows = []
        for r in records:
            lat, lon = self._get_geo(r)
            rows.append((
                r.get("school_name") or r.get("name") or "",
                r.get("school_category") or r.get("category") or "",
                r.get("address") or "",
                lat, lon, fetched_at
            ))
        conn = sqlite3.connect(self.db_path)
        conn.execute("DELETE FROM schools")
        conn.executemany(
            "INSERT INTO schools (name, category, address, latitude, longitude, fetched_at) VALUES (?,?,?,?,?,?)",
            rows
        )
        conn.commit()
        conn.close()
        logger.info(f"Saved {len(rows)} schools.")

    # ------------------------------------------------------------------ #
    #  VPD Crime data (CSV download)
    # ------------------------------------------------------------------ #

    def fetch_crime_data(self, years: list[int] = None):
        if years is None:
            years = [2020, 2021, 2022, 2023, 2024, 2025]

        base_dir = os.path.dirname(os.path.abspath(__file__))
        vpd_dir = os.path.join(base_dir, "..", "spider_central_db", "vpd_crime")
        fetched_at = datetime.utcnow().isoformat()
        all_rows = []

        for year in years:
            filename = f"crimedata_csv_AllNeighbourhoods_{year}.csv"
            #filepath = os.path.join(vpd_dir, filename)
            filepath = self._ensure_vpd_csv(year, vpd_dir)

            if not os.path.exists(filepath):
                logger.warning(f"[VPD] Could not prepare CSV for year {year}")
                continue

            logger.info(f"[VPD] Reading {filename}...")
            with open(filepath, encoding="utf-8", errors="replace") as f:
                reader = csv.DictReader(f)
                for row in reader:
                    try:
                        lat = float(row.get("Latitude") or 0) or None
                        lon = float(row.get("Longitude") or 0) or None
                    except ValueError:
                        lat, lon = None, None

                    all_rows.append((
                        int(row.get("YEAR") or year),
                        int(row.get("MONTH") or 0),
                        int(row.get("DAY") or 0),
                        int(row.get("HOUR") or 0),
                        int(row.get("MINUTE") or 0),
                        row.get("TYPE") or "",
                        row.get("NEIGHBOURHOOD") or "",
                        row.get("HUNDRED_BLOCK") or "",
                        lat, lon,
                        fetched_at
                    ))

            logger.info(f"[VPD] {year}: {len(all_rows)} total rows so far")

        conn = sqlite3.connect(self.db_path)
        conn.execute("DELETE FROM crime_incidents")
        conn.executemany("""
            INSERT INTO crime_incidents
            (year, month, day, hour, minute, offence_type, neighbourhood,
            hundred_block, latitude, longitude, fetched_at)
            VALUES (?,?,?,?,?,?,?,?,?,?,?)
        """, all_rows)
        conn.commit()
        conn.close()
        logger.info(f"Saved {len(all_rows)} crime incidents.")

    # ------------------------------------------------------------------ #
    #  Main
    # ------------------------------------------------------------------ #

    def run(self):
        logger.info("=== Safety & Convenience Spider starting ===")
        self.fetch_transit_stations()
        self.fetch_parks()
        self.fetch_schools()
        self.fetch_crime_data()
        logger.info("=== Done ===")


    def _ensure_vpd_csv(self, year: int, target_dir: str) -> str | None:
        os.makedirs(target_dir, exist_ok=True)
        csv_name = f"crimedata_csv_AllNeighbourhoods_{year}.csv"
        csv_path = os.path.join(target_dir, csv_name)

        if os.path.exists(csv_path):
            return csv_path

        url = VPD_CSV_URL.format(year=year)
        try:
            r = requests.get(url, timeout=60)
            r.raise_for_status()
            with zipfile.ZipFile(io.BytesIO(r.content)) as zf:
                for member in zf.namelist():
                    if member.lower().endswith(".csv"):
                        zf.extract(member, target_dir)
                        extracted = os.path.join(target_dir, member)
                        if extracted != csv_path and os.path.exists(extracted):
                            os.replace(extracted, csv_path)
                        return csv_path
        except requests.RequestException as e:
            logger.error(f"[VPD] Download failed for {year}: {e}")
        except zipfile.BadZipFile as e:
            logger.error(f"[VPD] Bad zip for {year}: {e}")

        return None


if __name__ == "__main__":
    spider = SafetyConvenienceSpider()
    # Fetch last 3 years of crime data by default
    # Pass crime_years=[2024, 2025] etc. to override
    spider.run()
