import importlib.util
from pathlib import Path


def load_class_from_file(file_path, class_name):
    spec = importlib.util.spec_from_file_location(class_name, file_path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return getattr(module, class_name)


RealEstateScraper = load_class_from_file(
    Path("Modules/spiders/spider_vinni_change_me/web_scraper.py"),
    "RealEstateScraper"
)

ListingCSVStorage = load_class_from_file(
    Path("Modules/spiders/spider_vinni_change_me/listing_csv_storage.py"),
    "ListingCSVStorage"
)

ListingSQLiteStorage = load_class_from_file(
    Path("Modules/spiders/spider_vinni_change_me/listing_sqlite_storage.py"),
    "ListingSQLiteStorage"
)

def main():
    url = "https://www.rew.ca/properties/areas/vancouver-bc"

    scraper = RealEstateScraper(url)
    listings = scraper.run()

    print(f"Listings found: {len(listings)}")

    storage = ListingCSVStorage()
    storage.save(listings)
    
    sqlite_storage = ListingSQLiteStorage()
    sqlite_storage.save(listings)

    for listing in listings[:5]:
        print(listing.to_json())


if __name__ == "__main__":
    main()