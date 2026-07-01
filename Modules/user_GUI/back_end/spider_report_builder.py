from pathlib import Path
import sqlite3
from datetime import datetime
import json
import ollama

from Modules.user_GUI.back_end.spider_config import SPIDER_REPORT_CONFIG
from Modules.config.project_paths import SPIDER_RAW_DB_PATH

class SpiderReportBuilder:
    def __init__(self, db_path: Path = SPIDER_RAW_DB_PATH, model_name: str = "llama3.1"):
        self.db_path = Path(db_path)
        self.model_name = model_name

    def build_report(self, spider_key: str) -> dict:
        config = SPIDER_REPORT_CONFIG.get(spider_key)
        if not config:
            raise ValueError(f"No report config for spider: {spider_key}")

        source_label = config["source"]
        snapshot = self._load_snapshot(source_label)
        summary = self._generate_summary_with_ollama(config, snapshot)

        return {
            "type": "spider",
            "spider": spider_key,
            "title": f"{config['label']} Market Report",
            "summary": summary,
            "report_type": "market",
            "model_name": self.model_name,
            "stats": snapshot,
            "created_at": datetime.now().isoformat(),
        }

    def _load_snapshot(self, source_label: str) -> dict:
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cur = conn.cursor()

        total_active = cur.execute("""
            SELECT COUNT(*)
            FROM posts
            WHERE LOWER(source_website) = LOWER(?)
            AND post_active = 1
        """, (source_label,)).fetchone()[0]

        new_today = cur.execute("""
            SELECT COUNT(*)
            FROM posts
            WHERE LOWER(source_website) = LOWER(?)
            AND date(time_scraped) = date('now')
        """, (source_label,)).fetchone()[0]

        avg_price = cur.execute("""
            SELECT AVG(l.price_of_the_unit)
            FROM posts p
            JOIN listings l ON p.post_id = l.post_id
            WHERE LOWER(p.source_website) = LOWER(?)
            AND l.price_of_the_unit IS NOT NULL
        """, (source_label,)).fetchone()[0]

        top_areas = cur.execute("""
            SELECT l.city_general_area, COUNT(*) AS listing_count
            FROM posts p
            JOIN listings l ON p.post_id = l.post_id
            WHERE LOWER(p.source_website) = LOWER(?)
            AND l.city_general_area IS NOT NULL
            AND TRIM(l.city_general_area) <> ''
            GROUP BY l.city_general_area
            ORDER BY listing_count DESC
            LIMIT 5
        """, (source_label,)).fetchall()

        sample_rows = cur.execute("""
            SELECT l.user_post_title, l.city_general_area, l.price_of_the_unit, u.bed_and_bath
            FROM posts p
            JOIN listings l ON p.post_id = l.post_id
            LEFT JOIN unit_details u ON p.post_id = u.post_id
            WHERE LOWER(p.source_website) = LOWER(?)
            ORDER BY p.time_scraped DESC
            LIMIT 10
        """, (source_label,)).fetchall()

        conn.close()

        return {
            "total_active": total_active,
            "new_today": new_today,
            "avg_price": round(avg_price, 2) if avg_price else None,
            "top_areas": [dict(r) for r in top_areas],
            "sample_rows": [dict(r) for r in sample_rows],
        }

    def _generate_summary_with_ollama(self, config: dict, snapshot: dict) -> str:
        prompt = f"""
You are a real estate rental market analyst.

Create a concise but insightful market report for {config['label']} using only the data below.
Do not invent facts.
Mention activity level, pricing, neighborhood concentration, and notable patterns.
Write 2 short paragraphs in professional language.

DATA:
{json.dumps(snapshot, indent=2)}
"""
        response = ollama.generate(
            model=self.model_name,
            prompt=prompt,
        )
        return response["response"].strip()