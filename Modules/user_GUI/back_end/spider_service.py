import sys
from pathlib import Path
from importlib import import_module
from Modules.user_GUI.back_end.spider_config import SPIDER_REGISTRY
from dataclasses import dataclass
from datetime import datetime
import subprocess
import uuid
import logging
import shlex


from scrapy import signals
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
    before_count: int = 0
    after_count: int = 0
    added_count: int = 0
    log_path: str | None = None
    returncode: int | None = None

RUNNING_JOBS: dict[str, SpiderJob] = {}

PROJECT_ROOT = Path(__file__).resolve().parents[3]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))


LOG_DIR = PROJECT_ROOT / "spider_logs"
LOG_DIR.mkdir(parents=True, exist_ok=True)


logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

if not logger.handlers:
    formatter = logging.Formatter(
        "%(asctime)s [%(levelname)s] %(name)s: %(message)s"
    )

    file_handler = logging.FileHandler(LOG_DIR / "spider_service.log", encoding="utf-8")
    file_handler.setFormatter(formatter)

    stream_handler = logging.StreamHandler()
    stream_handler.setFormatter(formatter)

    logger.addHandler(file_handler)
    logger.addHandler(stream_handler)

def get_available_spiders():
    return [
        {"key": key, "label": value["label"]}
        for key, value in SPIDER_REGISTRY.items()
    ]

def start_spider_job(spider_key: str) -> SpiderJob:
    spider_info = SPIDER_REGISTRY.get(spider_key)
    if not spider_info:
        raise ValueError(f"Unknown spider: {spider_key}")

    mode = spider_info["mode"]
    module_name = spider_info["module"]
    class_name = spider_info["class"]
    settings_module = spider_info.get("settings_module")

    command = [
        sys.executable,
        "-m",
        "Modules.user_GUI.back_end.spider_runner",
        "--spider-key",
        spider_key,
    ]

    if settings_module:
        command += ["--settings-module", settings_module]

    return start_spider_subprocess(command, spider_key)


def abort_spider_job(job_id: str) -> bool:
    job = RUNNING_JOBS.get(job_id)
    if not job or job.status != "running":
        return False

    try:
        job.process.terminate()
        job.status = "aborted"
        job.finished_at = datetime.utcnow().isoformat()
        logger.warning(
            "Spider job aborted: spider=%s job_id=%s",
            job.spider_name, job.job_id
        )

        if job.log_path:
            with open(job.log_path, "a", encoding="utf-8") as f:
                f.write(
                    f"\n\n[JOB-END] status=aborted finished_at={job.finished_at}\n"
                )

        return True
    except Exception:
        logger.exception("Failed to abort job_id=%s", job_id)
        raise

def start_spider_subprocess(command: list[str], spider_name: str) -> SpiderJob:
    job_id = str(uuid.uuid4())
    started_at = datetime.utcnow().isoformat()
    safe_name = spider_name.replace(" ", "_").lower()
    log_path = LOG_DIR / f"{safe_name}_{job_id}.log"

    logger.info("Starting spider '%s' with job_id=%s", spider_name, job_id)
    logger.info("Command: %s", command)
    logger.info("Subprocess log path: %s", log_path)

    try:
        log_file = open(log_path, "w", encoding="utf-8")
        log_file.write(f"STARTED_AT: {started_at}\n")
        log_file.write("COMMAND: " + " ".join(shlex.quote(x) for x in command) + "\n\n")
        log_file.flush()

        proc = subprocess.Popen(
            command,
            cwd=str(PROJECT_ROOT),
            stdout=log_file,
            stderr=subprocess.STDOUT,
            text=True,
            shell=False,
        )

        job = SpiderJob(
            job_id=job_id,
            spider_name=spider_name,
            process=proc,
            status="running",
            started_at=started_at,
            log_path=str(log_path),
        )

        RUNNING_JOBS[job_id] = job
        return job

    except Exception:
        logger.exception("Failed to start subprocess for spider '%s'", spider_name)
        raise

def run_scrapy_spider(spider_cls, settings_module: str | None = None):
    settings = Settings()
    if settings_module:
        settings.setmodule(settings_module, priority="project")

    process = CrawlerProcess(settings)
    crawler = process.create_crawler(spider_cls)

    state = {
        "closed_reason": None,
        "spider_error_count": 0,
    }

    def on_spider_error(failure, response, spider):
        state["spider_error_count"] += 1

    def on_spider_closed(spider, reason):
        state["closed_reason"] = reason

    crawler.signals.connect(on_spider_error, signal=signals.spider_error)
    crawler.signals.connect(on_spider_closed, signal=signals.spider_closed)

    process.crawl(crawler)
    process.start(stop_after_crawl=True, install_signal_handlers=False)

    stats = crawler.stats.get_stats()
    spider_exceptions = stats.get("spider_exceptions/count", 0)

    success = (
        state["closed_reason"] == "finished"
        and state["spider_error_count"] == 0
        and spider_exceptions == 0
    )

    return {
        "status": "success" if success else "error",
        "message": f"{spider_cls.__name__} closed with reason={state['closed_reason']}",
        "stats": {
            "finish_reason": state["closed_reason"],
            "spider_exceptions": spider_exceptions,
        },
    }

def refresh_job_status(job: SpiderJob):
    try:
        rc = job.process.poll()

        if rc is None:
            job.status = "running"
            return job

        job.returncode = rc
        job.finished_at = datetime.utcnow().isoformat()

        if rc == 0:
            job.status = "completed"
            logger.info(
                "Spider job completed: spider=%s job_id=%s returncode=%s",
                job.spider_name, job.job_id, rc
            )
        else:
            job.status = "failed"
            logger.error(
                "Spider job failed: spider=%s job_id=%s returncode=%s log_path=%s",
                job.spider_name, job.job_id, rc, job.log_path
            )

        if job.log_path:
            with open(job.log_path, "a", encoding="utf-8") as f:
                f.write(
                    f"\n\n[JOB-END] status={job.status} "
                    f"returncode={rc} finished_at={job.finished_at}\n"
                )

        return job

    except Exception:
        logger.exception("Failed while refreshing status for job_id=%s", job.job_id)
        raise

def run_spider_by_key(spider_key: str):
    spider_info = SPIDER_REGISTRY.get(spider_key)
    if not spider_info:
        raise ValueError(f"Unknown spider: {spider_key}")

    module_name = spider_info["module"]
    class_name = spider_info["class"]
    settings_module = spider_info.get("settings_module")

    logger.info(
        "Running spider by key=%s module=%s class=%s settings_module=%s",
        spider_key, module_name, class_name, settings_module
    )

    try:
        module = import_module(module_name)
        spider_cls = getattr(module, class_name)
    except Exception:
        logger.exception(
            "Failed loading spider key=%s module=%s class=%s",
            spider_key, module_name, class_name
        )
        raise

    try:
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
    except Exception:
        logger.exception("Spider execution failed for key=%s", spider_key)
        raise

    logger.info("Spider result for key=%s: %s", spider_key, result)

    return {
        "status": result["status"],
        "spider": spider_key,
        "message": f"{spider_info['label']}: {result['message']}",
        "result": result,
    }