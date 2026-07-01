"""
Status Checker Spider
=====================
Dedicated spider for checking if previously scraped listings are still active.

Flow:
    1. Reads all listing URLs from DB via Post_Data().get_urls()
    2. For each URL, sends a lightweight request with rotating user agent
    3. Checks if the page is still active or removed (404 / "There is nothing here")
    4. Updates post_status via Post_Data().update_post_last_active()

Per team decision (7/1/2026): status checking is a separate spider,
not embedded in individual scrapers. Named "status_checker" per Chris.

Usage:
    cd C:/Users/Philip/Documents/GitHub/4260_presentation
    scrapy runspider Modules/spiders/status_checker/status_checker.py
"""

import scrapy
import sys
import os


class StatusCheckerSpider(scrapy.Spider):

    name = "status_checker"
    allowed_domains = []

    custom_settings = {
        "CONCURRENT_REQUESTS_PER_DOMAIN": 1,
        "DOWNLOAD_DELAY": 2,
        "RANDOMIZE_DOWNLOAD_DELAY": True,
        "ROBOTSTXT_OBEY": False,
        "LOG_LEVEL": "INFO",
        "FEED_EXPORT_ENCODING": "utf-8",
    }

    def __get_project_root(self):
        """Return absolute path to project root (folder containing Modules/)."""
        return os.path.abspath(
            os.path.join(os.path.dirname(__file__), "..", "..", "..")
        )

    def __add_project_to_path(self):
        project_root = self.__get_project_root()
        if project_root not in sys.path:
            sys.path.insert(0, project_root)

    def __get_post_data(self):
        """Import Post_Data dynamically from project root."""
        self.__add_project_to_path()
        from Modules.spiders.spider_default_obj.spider_default_obj import Post_Data
        return Post_Data

    def __get_user_agent(self):
        """Get a random user agent from UserAgentFactory."""
        self.__add_project_to_path()
        from Modules.spiders.spider_default_obj.spider_user_agent_factor import UserAgentFactory
        return UserAgentFactory().get()

    async def start(self):
        """
        Fetch all listing URLs from DB and send a request for each.
        Uses Scrapy 2.x async start() instead of start_requests().
        Post_Data().get_urls() returns rows of (id, post_url, scraped_at).
        """
        self.logger.info("[status_checker] Starting — fetching URLs from DB...")

        Post_Data = self.__get_post_data()
        rows = Post_Data().get_urls()

        count = len(rows) if rows else 0
        self.logger.info(f"[status_checker] Found {count} listings to check.")

        if not rows:
            self.logger.warning("[status_checker] No listings found in DB.")
            return

        for row in rows:
            row_id, post_url, scraped_at = row[0], row[1], row[2]

            if not post_url:
                continue

            yield scrapy.Request(
                url=post_url,
                callback=self.check_status,
                cb_kwargs={"row_id": row_id, "scraped_at": scraped_at},
                errback=self.handle_error,
                meta={"row_id": row_id, "scraped_at": scraped_at},
                headers={"User-Agent": self.__get_user_agent()},
            )

    def check_status(self, response, row_id, scraped_at):
        """
        Check if the listing page is still active.
        """
        removed_phrases = [
            "there is nothing here",
            "this listing has been removed",
            "ad has been removed",
            "page not found",
            "listing is no longer available",
        ]

        page_text = response.text.lower()
        is_removed = (
            response.status == 404
            or any(phrase in page_text for phrase in removed_phrases)
        )

        active_post = not is_removed

        Post_Data = self.__get_post_data()
        Post_Data().update_post_last_active(
            scraped_at=scraped_at,
            active_post=active_post,
            row_id=row_id,
        )

        status_str = "ACTIVE" if active_post else "REMOVED"
        self.logger.info(
            f"[status_checker] row_id={row_id} | {status_str} | {response.url}"
        )

    def handle_error(self, failure):
        """Handle request errors — treat as potentially removed."""
        request = failure.request
        row_id = request.meta.get("row_id")
        scraped_at = request.meta.get("scraped_at")

        self.logger.warning(
            f"[status_checker] Request failed for row_id={row_id}: {failure.value}"
        )

        if row_id and scraped_at:
            Post_Data = self.__get_post_data()
            Post_Data().update_post_last_active(
                scraped_at=scraped_at,
                active_post=False,
                row_id=row_id,
            )