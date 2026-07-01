import sys
from pathlib import Path
from importlib import import_module
from Modules.user_GUI.back_end.spider_config import SPIDER_REGISTRY
from dataclasses import dataclass
from datetime import datetime
import subprocess
import uuid
from scrapy.crawler import CrawlerProcess
from scrapy.settings import Settings

@dataclass
class SpiderJob:
    job_id: str
    spider_name: str
    process: subprocess.Popen
    status: str
    started_at: str
    finished_at: str | None = None
    error: str | None = None

RUNNING_JOBS: dict[str, SpiderJob] = {}

PROJECT_ROOT = Path(__file__).resolve().parents[3]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

def get_available_spiders():
    return [
        {"key": key, "label": value["label"]}
        for key, value in SPIDER_REGISTRY.items()
    ]

def start_spider_subprocess(command: list[str], spider_name: str) -> SpiderJob:
    job_id = str(uuid.uuid4())
    proc = subprocess.Popen(command)
    job = SpiderJob(
        job_id=job_id,
        spider_name=spider_name,
        process=proc,
        status="running",
        started_at=datetime.utcnow().isoformat(),
    )
    RUNNING_JOBS[job_id] = job
    return job

def abort_spider(job_id: str) -> bool:
    job = RUNNING_JOBS.get(job_id)
    if not job or job.status != "running":
        return False

    job.process.terminate()
    job.status = "aborted"
    job.finished_at = datetime.utcnow().isoformat()
    return True


def run_scrapy_spider(spider_cls, settings_module: str | None = None):
    settings = Settings()
    if settings_module:
        settings.setmodule(settings_module, priority="project")

    process = CrawlerProcess(settings)
    process.crawl(spider_cls)
    process.start(stop_after_crawl=True, install_signal_handlers=False)

    return {
        "status": "success",
        "message": f"{spider_cls.__name__} completed.",
    }


def run_spider_by_key(spider_key: str):
    spider_info = SPIDER_REGISTRY.get(spider_key)
    if not spider_info:
        raise ValueError(f"Unknown spider: {spider_key}")

    module_name = spider_info["module"]
    class_name = spider_info["class"]
    settings_module = spider_info.get("settings_module")

    try:
        module = import_module(module_name)
    except Exception as e:
        raise ImportError(f"Failed to import module '{module_name}': {e}") from e
    
    try:
        spider_cls = getattr(module, class_name)
    except AttributeError as e:
        available = [name for name in dir(module) if not name.startswith("_")]
        raise AttributeError(
            f"Module '{module_name}' has no attribute '{class_name}'. "
            f"Available names: {available}"
        ) from e

    if spider_info["mode"] == "scrapy":
        result = run_scrapy_spider(spider_cls, settings_module=settings_module)
    elif spider_info["mode"] == "direct":
        spider = spider_cls()
        spider.run()
        result = {
            "status": "success",
            "message": f"{class_name} completed.",
        }
    else:
        raise ValueError(f"Unsupported spider mode: {spider_info['mode']}")

    return {
        "status": "success",
        "spider": spider_key,
        "message": f"{spider_info['label']} completed successfully.",
        "result": result,
    }