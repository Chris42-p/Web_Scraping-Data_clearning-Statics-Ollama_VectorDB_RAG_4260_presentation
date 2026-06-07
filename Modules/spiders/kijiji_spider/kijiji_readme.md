# Kijiji Vancouver Rental Spider

## Why / 為什麼這樣做

Kijiji is one of Canada's largest rental listing platforms. Scraping Vancouver
rental data allows us to:

- Track average rent prices by neighbourhood
- Visualize rental listing density on a map (integrates with Chris's map feature)
- Measure market speed (how long listings stay active)
- Compare rental prices over time across neighbourhoods

**Address + lat/lng data** is a key field — collected specifically to support
the planned map overlay showing regional rental prices (similar to Zillow heat map).

---

## How / 如何實作

- Uses `requests` + `BeautifulSoup` (no Selenium required)
- Kijiji listing cards use `li[data-listing-id]` for unique IDs
- Search results page → neighbourhood-level address
- Detail page scraper → full street address + geocoded lat/lng
- Geocoding uses **Nominatim** (free, no API key) by default
- Optionally supports **Google Maps Geocoding API** (more accurate)
- Polite delays between requests to avoid rate limiting

### File Structure

```
Modules/spiders/
├── kijiji_spider.py              ← Main spider (search results)
├── kijiji_detail_scraper.py      ← Detail page scraper + geocoding
├── kijiji_listing_object.py      ← Data object for each listing
├── kijiji_spider_interface.py    ← Interface + CONST hardcoded values
└── kijiji_readme.md              ← This file
```

### Usage

```python
from Modules.spiders.kijiji_spider import KijijiRentalSpider
from Modules.spiders.kijiji_detail_scraper import KijijiDetailScraper

# Step 1: scrape search results (fast)
spider = KijijiRentalSpider()
listings = spider.run(max_pages=3)

# Step 2: enrich with full address + lat/lng (slow — one request per listing)
detail_scraper = KijijiDetailScraper()
listings = detail_scraper.enrich_listings(listings, delay=2.0)

# Step 3: export to CSV
spider.export_csv(listings, "scraped_data/kijiji_rentals.csv")
```

### Using Google Maps for better geocoding

In `kijiji_spider_interface.py`, set:
```python
"USE_GOOGLE_GEOCODING": True,
"GOOGLE_MAPS_API_KEY": "your_key_here",
```

Then:
```python
detail_scraper = KijijiDetailScraper(use_google=True, google_api_key="your_key")
```

---

## Fields Collected / 抓取的欄位

| Field | Source | Description |
|---|---|---|
| `title` | Search page | Listing title |
| `listing_url` | Search page | Full URL to listing |
| `listing_id` | Search page | Kijiji unique ID |
| `address` | Detail page | Full street address (for map) |
| `neighbourhood` | Search page | Neighbourhood |
| `city` | Hardcoded | Always "Vancouver" |
| `province` | Hardcoded | Always "BC" |
| `latitude` | Geocoding | For map pin placement |
| `longitude` | Geocoding | For map pin placement |
| `price` | Search page | Monthly rent |
| `bedrooms` | Search page | Number of bedrooms |
| `bathrooms` | Search page | Number of bathrooms |
| `square_feet` | Search page | Unit size if listed |
| `property_type` | Search page | Apartment, House, etc. |
| `furnished` | Search page | Furnished / Unfurnished |
| `pets_allowed` | Search page | Yes / No |
| `parking` | Detail page | Included / N/A |
| `description` | Detail page | Full listing text |
| `first_seen` | Auto | Date first scraped |
| `last_seen` | Auto | Date last seen active |

---

## Bugs / 已知問題

- Search results page may only show neighbourhood (not full street address)
  → Detail scraper required for full address
- Kijiji may update HTML structure, breaking CSS selectors
- Nominatim geocoding may fail for ambiguous addresses
- Rate limiting: too many requests may cause temporary IP block
- `latitude`/`longitude` = "N/A" if address extraction fails

---

## Future Improvements

- Store results in project SQLite DB (table: `kijiji_vancouver_rentals`)
- Add price history tracking
- Schedule regular scraping to track market trends
- Integrate with Chris's map feature using stored lat/lng
