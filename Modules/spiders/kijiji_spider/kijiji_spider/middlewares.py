# Kijiji Spider Middlewares
# Following Spider_Template_copy_paste pattern from Chris
# User agent rotation via UserAgentFactory from spider_default_obj

from scrapy import signals
from itemadapter import ItemAdapter

import sys, os


from pathlib import Path
import sys

#==========================




class UserAgentRotationMiddleware:

    @classmethod
    def from_crawler(cls, crawler):
        s = cls()
        crawler.signals.connect(s.spider_opened, signal=signals.spider_opened)
        return s

    def __init__(self):
        #== IMPORT THE DEFUALT OBJECT DYNAMICALLY =====
        from pathlib import Path
        import sys
        current = Path(__file__).resolve()
        for parent in current.parents:
            if (parent / "Modules").exists():
                if str(parent) not in sys.path:
                    sys.path.append(str(parent))
                break
        from Modules.spiders.spider_default_obj.spider_user_agent_factor import UserAgentFactory
        self.user_agent = UserAgentFactory()

    def process_request(self, request, spider):
        headers = self.user_agent.get_headers()
        for key, value in headers.items():
            request.headers[key] = value
        return None

    def spider_opened(self, spider):
        spider.logger.info("Spider opened: %s" % spider.name)


class KijijiSpiderMiddleware:

    @classmethod
    def from_crawler(cls, crawler):
        s = cls()
        crawler.signals.connect(s.spider_opened, signal=signals.spider_opened)
        return s

    def process_spider_input(self, response, spider):
        return None

    def process_spider_output(self, response, result, spider):
        for i in result:
            yield i

    def process_spider_exception(self, response, exception, spider):
        pass

    async def process_start(self, start):
        async for item_or_request in start:
            yield item_or_request

    def spider_opened(self, spider):
        spider.logger.info("Spider opened: %s" % spider.name)


class KijijiSpiderDownloaderMiddleware:

    @classmethod
    def from_crawler(cls, crawler):
        s = cls()
        crawler.signals.connect(s.spider_opened, signal=signals.spider_opened)
        return s

    def process_request(self, request, spider):
        return None

    def process_response(self, request, response, spider):
        return response

    def process_exception(self, request, exception, spider):
        pass

    def spider_opened(self, spider):
        spider.logger.info("Spider opened: %s" % spider.name)
