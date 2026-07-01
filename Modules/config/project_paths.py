from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]

APP_DB_PATH = (
    PROJECT_ROOT
    / "Modules"
    / "engine_injesting"
    / "data_base"
    / "my_sql_db.db"
)

SPIDER_RAW_DB_PATH = (
    PROJECT_ROOT
    / "Modules"
    / "spiders"
    / "spider_default_obj"
    / "spider_central_db"
    / "spider_central.db"
)

SPIDER_REPORTS_JSON_PATH = (
    PROJECT_ROOT
    / "Modules"
    / "engine_injesting"
    / "data_base"
    / "spider_reports.json"
)