from scrapy import signals
import sys
from pathlib import Path

sys.path.append(
    str(Path(__file__).resolve().parents[2] / "spider_default_obj")
)

from Modules.spiders.spider_default_obj.spider_user_agent_factor import UserAgentFactory


class UserAgentRotationMiddleware:

    @classmethod
    def from_crawler(cls, crawler):
        middleware = cls()
        crawler.signals.connect(
            middleware.spider_opened,
            signal=signals.spider_opened
        )
        return middleware

    def __init__(self):
        self.user_agent_factory = UserAgentFactory()

    def process_request(self, request, spider):
        headers = self.user_agent_factory.get_headers()

        for key, value in headers.items():
            request.headers[key] = value

        request.headers["Referer"] = "https://www.rew.ca/"
        return None

    def spider_opened(self, spider):
        spider.logger.info(f"Spider opened: {spider.name}")