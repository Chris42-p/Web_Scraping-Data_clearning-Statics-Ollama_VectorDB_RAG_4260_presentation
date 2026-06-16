from importlib import import_module
import importlib.util
from pathlib import Path


def get_available_spiders():
    return [
        {"key": "safety_convenience", "label": "Safety & Convenience Spider"},
        {"key": "rew", "label": "REW Spider"},
    ]


def run_spider_by_key(spider_key: str):
    if spider_key == "safety_convenience":
        module = import_module(
            "Modules.spiders.safety_convenience_spider.safety_convenience_spider"
        )
        spider = module.SafetyConvenienceSpider()
        spider.run()
        return {
            "status": "success",
            "spider": spider_key,
            "message": "Safety & Convenience spider completed.",
        }

    if spider_key == "rew":
        return run_rew_spider()

    raise ValueError(f"Unknown spider: {spider_key}")


def load_rew_spider_class():
    project_root = Path(__file__).resolve().parents[3]
    spider_path = project_root / "Modules" / "spiders" / "Data" / "spider_vinni_change_me" / "rew_spider.py"

    if not spider_path.exists():
        raise FileNotFoundError(f"REW spider file not found at: {spider_path}")

    spec = importlib.util.spec_from_file_location("rew_spider", spider_path)
    if spec is None or spec.loader is None:
        raise ImportError(f"Could not load REW spider spec from: {spider_path}")

    rew_module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(rew_module)

    if not hasattr(rew_module, "REWSpider"):
        raise ImportError("REWSpider class not found in rew_spider.py")

    return rew_module.REWSpider


def run_rew_spider():
    from scrapy.crawler import CrawlerProcess
    from scrapy.utils.project import get_project_settings

    REWSpider = load_rew_spider_class()

    settings = get_project_settings()
    process = CrawlerProcess(settings)
    process.crawl(REWSpider)
    process.start()

    return {
        "status": "success",
        "spider": "rew",
        "message": "REW spider completed.",
    }