# Status Checker Spider

Checks if previously scraped listings are still active and updates `post_status` in the DB.

## What it does

1. Reads all listing URLs from `listings_db.db` via `Post_Data().get_urls()`
2. Sends a request to each URL with a rotating user agent
3. Checks if the page is still active or removed (404 / "There is nothing here")
4. Updates `post_status` via `Post_Data().update_post_last_active()`

## Requirements

Make sure Docker is running (for Ollama):
```
docker compose up -d
```

## How to run

Always run from the **project root**:

```
cd C:/Users/Philip/Documents/GitHub/4260_presentation
scrapy runspider Modules/spiders/status_checker/status_checker.py
```

## Expected output

```
[status_checker] Found 548 listings to check.
[status_checker] row_id=1 | ACTIVE | https://www.kijiji.ca/...
[status_checker] row_id=2 | REMOVED | https://www.kijiji.ca/...
```

## Notes

- Run from project root only — not from inside the `status_checker` folder
- User agent rotation is built in (reduces 403 blocks)
- 410 Gone = listing has been removed from the site (expected)
- Recommended schedule: once per week (aligns with spider re-scrape cycle)
