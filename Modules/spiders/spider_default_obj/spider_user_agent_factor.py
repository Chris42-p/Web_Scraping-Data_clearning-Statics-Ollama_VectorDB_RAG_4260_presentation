import random

class UserAgentFactory:

    BROWSER_VERSIONS = {
        "chrome": list(range(110, 125)),
        "firefox": list(range(115, 126)),
        "safari": ["16.4", "16.5", "17.0", "17.1", "17.2", "17.3", "17.4"],
    }

    OS_TEMPLATES = {
        "windows": [
            "Windows NT 10.0; Win64; x64",
            "Windows NT 11.0; Win64; x64",
        ],
        "mac": [
            "Macintosh; Intel Mac OS X 10_15_7",
            "Macintosh; Intel Mac OS X 11_0_0",
            "Macintosh; Intel Mac OS X 12_0_0",
            "Macintosh; Intel Mac OS X 13_0_0",
            "Macintosh; Intel Mac OS X 14_0_0",
        ],
        "linux": [
            "X11; Linux x86_64",
            "X11; Ubuntu; Linux x86_64",
        ],
        "iphone": [
            "iPhone; CPU iPhone OS 16_0 like Mac OS X",
            "iPhone; CPU iPhone OS 17_0 like Mac OS X",
            "iPhone; CPU iPhone OS 17_4 like Mac OS X",
        ],
    }

    def _chrome(self):
        version = random.choice(self.BROWSER_VERSIONS["chrome"])
        os = random.choice([
            *self.OS_TEMPLATES["windows"],
            *self.OS_TEMPLATES["mac"],
            *self.OS_TEMPLATES["linux"],
        ])
        return (
            f"Mozilla/5.0 ({os}) "
            f"AppleWebKit/537.36 (KHTML, like Gecko) "
            f"Chrome/{version}.0.0.0 Safari/537.36"
        )

    def _firefox(self):
        version = random.choice(self.BROWSER_VERSIONS["firefox"])
        os = random.choice([
            *self.OS_TEMPLATES["windows"],
            *self.OS_TEMPLATES["mac"],
            *self.OS_TEMPLATES["linux"],
        ])
        return (
            f"Mozilla/5.0 ({os}; rv:{version}.0) "
            f"Gecko/20100101 Firefox/{version}.0"
        )

    def _safari(self):
        version = random.choice(self.BROWSER_VERSIONS["safari"])
        os = random.choice([
            *self.OS_TEMPLATES["mac"],
            *self.OS_TEMPLATES["iphone"],
        ])
        webkit = "605.1.15"
        return (
            f"Mozilla/5.0 ({os}) "
            f"AppleWebKit/{webkit} (KHTML, like Gecko) "
            f"Version/{version} Safari/{webkit}"
        )

    def get(self, browser=None):
        """Generate a random valid user agent"""
        generators = {
            "chrome":  self._chrome,
            "firefox": self._firefox,
            "safari":  self._safari,
        }
        if browser:
            return generators[browser]()
        return random.choice(list(generators.values()))()

    def get_headers(self, browser=None):
        """Return full headers dict, not just user agent"""
        ua = self.get(browser)
        return {
            "User-Agent":      ua,
            "Accept-Language": random.choice([
                "en-US,en;q=0.9",
                "en-GB,en;q=0.9",
                "en-CA,en;q=0.8,fr-CA;q=0.7",
            ]),
            "Accept": (
                "text/html,application/xhtml+xml,"
                "application/xml;q=0.9,image/webp,*/*;q=0.8"
            ),
            "Accept-Encoding": "gzip, deflate, br",
            "Connection":      "keep-alive",
        }