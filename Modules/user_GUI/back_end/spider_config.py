SPIDER_REPORT_CONFIG = {
    "rew": {
        "label": "REW",
        "source": "REW.ca",
    },
    "kijiji": {
        "label": "Kijiji",
        "source": "Kijiji",
    },
    "craigslist": {
        "label": "Craigslist",
        "source": "Craigslist",
    },
    "realtylink": {
        "label": "Realtylink",
        "source": "Realtylink",
    },
    "safety_convenience": {
        "label": "Safety & Convenience",
        "source": "Safety & Convenience Spider",
    },
}

SPIDER_REGISTRY = {
    "rew": {
        "label": "REW Spider",
        "module": "Modules.spiders.rew_spider.rew_spider.spiders.rew_spider",
        "class": "RewSpider",
        "mode": "scrapy",
        "settings_module": "Modules.spiders.rew_spider.rew_spider.settings",
    },
    "kijiji": {
        "label": "Kijiji Spider",
        "module": "Modules.spiders.kijiji_spider.kijiji_spider.spiders.kijiji_rental_spider",
        "class": "KijijiRentalsSpider",
        "mode": "scrapy",
        "settings_module": "Modules.spiders.kijiji_spider.kijiji_spider.settings",
    },
    "realtylink": {
        "label": "RealtyLink Spider",
        "module": "Modules.spiders.realtylink.realtylink.spiders.realtylink_spider",
        "class": "RealtylinkSpiderSpider",
        "mode": "scrapy",
        "settings_module": "Modules.spiders.realtylink.realtylink.settings",
    },
    "craigslist": {
        "label": "Craigslist Spider",
        "module": "Modules.spiders.cragslist_spider.cragslist_spider.spiders.cragslist_spider",
        "class": "CregslistSpiderSpider",
        "mode": "scrapy",
        "settings_module": "Modules.spiders.cragslist_spider.cragslist_spider.settings",
    },
    "safety_convenience": {
        "label": "Safety & Convenience Spider",
        "module": "Modules.spiders.safety_convenience_spider.safety_convenience_spider",
        "class": "SafetyConvenienceSpider",
        "mode": "direct",
    },
}

SPIDER_CONFIGS = {
    "rew": {"enabled": False, "intervalMinutes": 30, "region": "Vancouver", "keywords": "rental apartment", "maxPages": 5},
    "kijiji": {"enabled": False, "intervalMinutes": 30, "region": "Vancouver", "keywords": "rental apartment", "maxPages": 5},
    "realtylink": {"enabled": False, "intervalMinutes": 30, "region": "Vancouver", "keywords": "rental apartment", "maxPages": 5},
    "craigslist": {"enabled": False, "intervalMinutes": 60, "region": "Vancouver", "keywords": "rental apartment", "maxPages": 5},
    "safety_convenience": {"enabled": False, "intervalMinutes": 120, "region": "Vancouver", "keywords": "rental apartment", "maxPages": 5},
}

SPIDER_STATUS_CONFIG = {
    "rew": {"lastRunAt": None, "nextRunAt": None, "isRunning": False},
    "kijiji": {"lastRunAt": None, "nextRunAt": None, "isRunning": False},
    "realtylink": {"lastRunAt": None, "nextRunAt": None, "isRunning": False},
    "craigslist": {"lastRunAt": None, "nextRunAt": None, "isRunning": False},
    "safety_convenience": {"lastRunAt": None, "nextRunAt": None, "isRunning": False},
}