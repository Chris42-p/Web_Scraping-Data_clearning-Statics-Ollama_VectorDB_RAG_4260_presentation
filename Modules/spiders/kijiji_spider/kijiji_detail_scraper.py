"""
Kijiji Listing Detail Scraper

Purpose:
    Scrapes the individual Kijiji listing page to get:
        - Full street address (for map integration)
        - Latitude / Longitude via geocoding (Google Maps or Nominatim)
        - Full description
        - Additional amenities

    The main KijijiRentalSpider collects basic info from the search results
    page. This detail scraper enriches each listing with the full address
    needed for Chris's map feature.

Implementation Notes:
    - Kijiji listing detail pages contain the address in a
      data-address or location section element
    - Geocoding converts "123 Main St, Vancouver, BC" → lat/lng
    - Uses Nominatim (free, no API key) by default
    - Optionally supports Google Maps Geocoding API (more accurate)

Why geocoding?
    Lat/lng coordinates are required to plot listings on a map.
    Without them, we can only show neighbourhood-level data.
    With them, Chris's map feature can show exact pin locations
    with price labels — similar to Zillow's map view.

Geocoding options:
    1. Nominatim (OpenStreetMap) — free, no API key, rate limited to 1 req/sec
    2. Google Maps Geocoding API — paid, more accurate, faster
    Set USE_GOOGLE_GEOCODING = True in kijiji_spider_interface.py
    and provide GOOGLE_MAPS_API_KEY to use Google.
"""

import requests
from bs4 import BeautifulSoup
import time
import re


class KijijiDetailScraper:
    """
    Scrapes detailed information from a single Kijiji listing page,
    including full address and geocoded lat/lng for map integration.

    Usage:
        scraper = KijijiDetailScraper()
        details = scraper.scrape("https://www.kijiji.ca/v-apartments-condos/...")
        print(details["address"])    # "123 Main St, Kitsilano, Vancouver, BC"
        print(details["latitude"])   # "49.2688"
        print(details["longitude"])  # "-123.1540"
    """

    HEADERS = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
        "Accept-Language": "en-CA,en;q=0.9",
    }

    GEOCODE_DELAY = 1.1  # Nominatim requires 1 request/sec max

    def __init__(self, use_google: bool = False, google_api_key: str = None):
        """
        Args:
            use_google: Use Google Maps Geocoding API instead of Nominatim
            google_api_key: Required if use_google=True
        """
        self.use_google = use_google
        self.google_api_key = google_api_key

    def __fetch_html(self, url: str) -> str:
        """Download HTML from a Kijiji listing detail page."""
        response = requests.get(url, headers=self.HEADERS, timeout=15)
        response.raise_for_status()
        return response.text

    def __extract_address(self, soup: BeautifulSoup) -> str:
        """
        Extract full address from Kijiji listing detail page.

        Kijiji shows address in multiple possible locations:
        - data-address attribute on a map element
        - A location/address section in the listing details
        - The listing description text itself
        """
        # Method 1: data-address attribute on map element
        map_el = soup.select_one("[data-address]")
        if map_el and map_el.get("data-address"):
            return map_el["data-address"].strip()

        # Method 2: address in a structured location section
        location_selectors = [
            "[class*='address']",
            "[class*='location']",
            "[itemprop='address']",
            "[class*='mapAddress']",
        ]
        for selector in location_selectors:
            el = soup.select_one(selector)
            if el:
                text = el.get_text(strip=True)
                if text and len(text) > 5:
                    return text

        # Method 3: look for address pattern in full page text
        page_text = soup.get_text(" ", strip=True)
        match = re.search(
            r"\d+\s+[A-Za-z]+(?:\s+[A-Za-z]+)?\s+(?:St|Ave|Rd|Blvd|Dr|Cres|Way|Lane|Pl|Court|Ct|Street|Avenue|Road|Drive)\b[^.]*(?:Vancouver|Burnaby|Richmond)[^.]*,\s*BC",
            page_text,
            re.IGNORECASE
        )
        if match:
            return match.group(0).strip()

        return "N/A"

    def __extract_full_description(self, soup: BeautifulSoup) -> str:
        """Extract full listing description text."""
        desc_selectors = [
            "[class*='description']",
            "[itemprop='description']",
            "[class*='descriptionContainer']",
        ]
        for selector in desc_selectors:
            el = soup.select_one(selector)
            if el:
                return el.get_text(" ", strip=True)[:1000]
        return "N/A"

    def __extract_amenities(self, soup: BeautifulSoup) -> dict:
        """
        Extract amenity checkboxes/tags from listing detail page.
        Returns dict of amenity name → True/False.
        """
        amenities = {
            "air_conditioning": False,
            "laundry_in_unit": False,
            "dishwasher": False,
            "parking_included": False,
            "elevator": False,
            "gym": False,
            "balcony": False,
            "wheelchair_accessible": False,
        }

        page_text = soup.get_text(" ", strip=True).lower()

        keyword_map = {
            "air_conditioning": ["air conditioning", "a/c", "ac unit", "central air"],
            "laundry_in_unit": ["in-suite laundry", "in suite laundry", "washer/dryer", "washer and dryer"],
            "dishwasher": ["dishwasher"],
            "parking_included": ["parking included", "parking spot", "underground parking"],
            "elevator": ["elevator"],
            "gym": ["gym", "fitness centre", "fitness center"],
            "balcony": ["balcony", "patio", "terrace"],
            "wheelchair_accessible": ["wheelchair", "accessible"],
        }

        for amenity, keywords in keyword_map.items():
            if any(kw in page_text for kw in keywords):
                amenities[amenity] = True

        return amenities

    def __geocode_nominatim(self, address: str) -> tuple[str, str]:
        """
        Convert address to lat/lng using Nominatim (OpenStreetMap).
        Free, no API key required. Rate limit: 1 request/second.

        Returns:
            (latitude, longitude) as strings, or ("N/A", "N/A")
        """
        if address == "N/A":
            return "N/A", "N/A"

        # Add Vancouver BC if not present for better accuracy
        query = address
        if "vancouver" not in address.lower():
            query = f"{address}, Vancouver, BC, Canada"

        try:
            url = "https://nominatim.openstreetmap.org/search"
            params = {
                "q": query,
                "format": "json",
                "limit": 1,
                "countrycodes": "ca",
            }
            headers = {
                "User-Agent": "CSIS4260-BigData-Project/1.0 (educational project)"
            }

            time.sleep(self.GEOCODE_DELAY)  # respect rate limit

            response = requests.get(url, params=params, headers=headers, timeout=10)
            data = response.json()

            if data:
                return str(data[0]["lat"]), str(data[0]["lon"])

        except Exception as e:
            print(f"Nominatim geocoding error for '{address}': {e}")

        return "N/A", "N/A"

    def __geocode_google(self, address: str) -> tuple[str, str]:
        """
        Convert address to lat/lng using Google Maps Geocoding API.
        Requires API key. More accurate than Nominatim.

        Returns:
            (latitude, longitude) as strings, or ("N/A", "N/A")
        """
        if address == "N/A" or not self.google_api_key:
            return "N/A", "N/A"

        try:
            url = "https://maps.googleapis.com/maps/api/geocode/json"
            params = {
                "address": f"{address}, Vancouver, BC, Canada",
                "key": self.google_api_key,
            }
            response = requests.get(url, params=params, timeout=10)
            data = response.json()

            if data["status"] == "OK":
                location = data["results"][0]["geometry"]["location"]
                return str(location["lat"]), str(location["lng"])

        except Exception as e:
            print(f"Google geocoding error for '{address}': {e}")

        return "N/A", "N/A"

    def __geocode(self, address: str) -> tuple[str, str]:
        """Route to correct geocoding provider based on config."""
        if self.use_google and self.google_api_key:
            return self.__geocode_google(address)
        return self.__geocode_nominatim(address)

    def scrape(self, url: str) -> dict:
        """
        Public controller — scrape detail page and return enriched data.

        Args:
            url: Full Kijiji listing URL

        Returns:
            dict with keys: address, latitude, longitude,
                           full_description, amenities
        """
        try:
            html = self.__fetch_html(url)
            soup = BeautifulSoup(html, "html.parser")

            address = self.__extract_address(soup)
            lat, lng = self.__geocode(address)

            return {
                "address": address,
                "latitude": lat,
                "longitude": lng,
                "full_description": self.__extract_full_description(soup),
                "amenities": self.__extract_amenities(soup),
            }

        except Exception as e:
            print(f"Error scraping detail page {url}: {e}")
            return {
                "address": "N/A",
                "latitude": "N/A",
                "longitude": "N/A",
                "full_description": "N/A",
                "amenities": {},
            }

    def enrich_listings(self, listings: list, delay: float = 2.0) -> list:
        """
        Public controller — enrich a list of KijijiListingObjects
        with full address and lat/lng from their detail pages.

        Args:
            listings: list of KijijiListingObject instances
            delay: seconds to wait between detail page requests

        Returns:
            same list with address, latitude, longitude updated
        """
        total = len(listings)
        for i, listing in enumerate(listings):
            if listing.listing_url == "N/A":
                continue

            print(f"Enriching {i+1}/{total}: {listing.listing_url}")

            details = self.scrape(listing.listing_url)

            # Only update address if we got something better
            if details["address"] != "N/A":
                listing.address = details["address"]

            listing.latitude = details["latitude"]
            listing.longitude = details["longitude"]

            if details["full_description"] != "N/A":
                listing.description = details["full_description"]

            # Flatten amenities into listing fields
            amenities = details.get("amenities", {})
            if amenities.get("parking_included"):
                listing.parking = "Included"

            time.sleep(delay)

        return listings
