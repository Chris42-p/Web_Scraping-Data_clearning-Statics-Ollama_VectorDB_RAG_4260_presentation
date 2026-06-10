"""
Listing Detail Scraper Module

This module is responsible for scraping the individual property page
from REW.ca.

The main listing scraper collects basic listing information from the
search results page. This detail scraper enriches each listing with
additional fields such as taxes, parking, year built, heating, cooling,
features, appliances, days on REW, and MLS number.
"""

import requests
from bs4 import BeautifulSoup
import time
import re


class ListingDetailScraper:
    """
    Scrapes detailed information from a single REW listing page.
    """

    def __init__(self):
        self.headers = {
            "User-Agent": "Mozilla/5.0"
        }

    def fetch_html(self, url):
        """
        Download the HTML content of a listing detail page.
        Adds a small delay and handles rate limiting.
        """

        time.sleep(2)

        response = requests.get(
            url,
            headers=self.headers,
            timeout=15
        )

        if response.status_code == 429:
            print(f"Rate limited. Skipping detail page: {url}")
            return ""

        response.raise_for_status()
        return response.text

    def extract_between(self, text, start_label, end_label):

        start_index = text.find(start_label)

        if start_index == -1:
            return "N/A"

        start_index += len(start_label)

        end_index = text.find(end_label, start_index)

        if end_index == -1:
            return "N/A"

        return text[start_index:end_index].strip()
    
    def clean_year_built(self, year_text):
        match = re.search(r"Built in (\d{4})", year_text)
        return match.group(1) if match else "N/A"

    def clean_building_age(self, year_text):
        match = re.search(r"\((\d+)\s+yrs old\)", year_text)
        return match.group(1) if match else "N/A"

    def scrape(self, url):
        """
        Scrape and return detailed fields from one listing URL.
        """
        html = self.fetch_html(url)

        if not html:
            return {}

        soup = BeautifulSoup(html, "html.parser")

        text = soup.get_text("\n", strip=True)

        year_info = self.extract_between(
            text,
            "Year Built",
            "Title"
        )

        broker = self.extract_between(
            text,
            "Primary Broker",
            "Secondary Agent"
        )

        if broker == "N/A":
            broker = self.extract_between(
                text,
                "Primary Broker",
                "Listing details"
            )


        return {
            "gross_taxes": self.extract_between(text, "Gross Taxes for 2025", "Home facts"),
            "parking_spaces": self.extract_between(text, "Parking Spaces", "Parking Details"),
            "parking_details": self.extract_between(text, "Parking Details", "Property Type"),
            "heating_type": self.extract_between(text, "Heating Type", "Cooling"),
            "cooling": self.extract_between(text, "Cooling", "Basement Details"),
            "basement_details": self.extract_between(text, "Basement Details", "Features"),
            "features": self.extract_between(text, "Features", "Amenities"),
            "appliances": self.extract_between(text, "Appliances", "Community"),
            "primary_agent": self.extract_between(text, "Primary Agent", "Primary Broker"),
            "primary_broker": broker,
            "days_on_rew": self.extract_between(text, "Days on REW","Property Views"),
            "mls_number": self.extract_between(text, "MLS® Number", "Source"),
            "amenities": self.extract_between(text,"Amenities","Appliances"),
            "building_age": self.clean_building_age(year_info),
            "year_built": self.clean_year_built(year_info)

        }