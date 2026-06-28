"""
Export all safety_convenience.db tables to CSV files.
Run from: Modules/spiders/safety_convenience_spider/
Output:  Modules/spiders/spider_central_db/csv/
"""

import sqlite3
import csv
import os

DB_PATH = os.path.join(os.path.dirname(__file__), "..", "spider_central_db", "safety_convenience.db")
OUTPUT_DIR = os.path.join(os.path.dirname(__file__), "..", "spider_central_db", "csv")

TABLES = ["transit_stations", "parks", "schools", "crime_incidents"]

def export_all():
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    conn = sqlite3.connect(DB_PATH)

    for table in TABLES:
        output_path = os.path.join(OUTPUT_DIR, f"{table}.csv")
        cursor = conn.execute(f"SELECT * FROM {table}")
        rows = cursor.fetchall()
        headers = [d[0] for d in cursor.description]

        with open(output_path, "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow(headers)
            writer.writerows(rows)

        print(f"Exported {len(rows)} rows → {output_path}")

    conn.close()
    print("Done.")

if __name__ == "__main__":
    export_all()