from importlib import import_module

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


def run_rew_spider():
    from scrapy.crawler import CrawlerProcess
    from scrapy.utils.project import get_project_settings
    from Modules.spiders.spider_vinni_change_me.rew_spider import REWSpider

    settings = get_project_settings()
    process = CrawlerProcess(settings)
    process.crawl(REWSpider)
    process.start()

    return {
        "status": "success",
        "spider": "rew",
        "message": "REW spider completed.",
    }