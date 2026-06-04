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
        """
        response = requests.get(
            url,
            headers=self.headers,
            timeout=15
        )

        response.raise_for_status()
        return response.text

    def extract_between(self, text, start_label, end_label):
        """
        Extract text between two labels.

        Example:
            Parking Spaces
            1
            Parking Details

        Returns:
            1
        """
        start_index = text.find(start_label)

        if start_index == -1:
            return "N/A"

        start_index += len(start_label)

        end_index = text.find(end_label, start_index)

        if end_index == -1:
            return text[start_index:].strip()

        return text[start_index:end_index].strip()

    def scrape(self, url):
        """
        Scrape and return detailed fields from one listing URL.
        """
        html = self.fetch_html(url)
        soup = BeautifulSoup(html, "html.parser")

        text = soup.get_text("\n", strip=True)

        return {
            "gross_taxes": self.extract_between(text, "Gross Taxes for 2025", "Home facts"),
            "parking_spaces": self.extract_between(text, "Parking Spaces", "Parking Details"),
            "parking_details": self.extract_between(text, "Parking Details", "Property Type"),
            "year_built": self.extract_between(text, "Year Built", "Title"),
            "heating_type": self.extract_between(text, "Heating Type", "Cooling"),
            "cooling": self.extract_between(text, "Cooling", "Basement Details"),
            "basement_details": self.extract_between(text, "Basement Details", "Features"),
            "features": self.extract_between(text, "Features", "Appliances"),
            "appliances": self.extract_between(text, "Appliances", "Community"),
            "primary_agent": self.extract_between(text, "Primary Agent", "Primary Broker"),
            "primary_broker": self.extract_between(text, "Primary Broker", "Secondary Agent"),
            "days_on_rew": self.extract_between(text, "Days on REW", "Property Views"),
            "mls_number": self.extract_between(text, "MLS® Number", "Source")
        }