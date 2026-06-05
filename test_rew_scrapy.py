import importlib.util
from scrapy.crawler import CrawlerProcess


spec = importlib.util.spec_from_file_location(
    "rew_spider",
    "Modules/engine_injesting/scrapy_spiders/rew_spider.py"
)

rew_module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(rew_module)

REWSpider = rew_module.REWSpider


def main():

    process = CrawlerProcess(settings={
        "FEEDS": {
            "scraped_data/rew_scrapy_output.json": {
                "format": "json",
                "overwrite": True
            }
        }
    })

    process.crawl(REWSpider)
    process.start()


if __name__ == "__main__":
    main()