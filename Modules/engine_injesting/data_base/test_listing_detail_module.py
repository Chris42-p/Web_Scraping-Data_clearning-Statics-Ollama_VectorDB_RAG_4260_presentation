import importlib.util
from pathlib import Path


def load_class_from_file(file_path, class_name):
    spec = importlib.util.spec_from_file_location(class_name, file_path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return getattr(module, class_name)


ListingDetailScraper = load_class_from_file(
    Path("Modules/engine_injesting/listing_detail_scraper.py"),
    "ListingDetailScraper"
)


def main():
    url = "https://www.rew.ca/properties/4327-perry-street-vancouver-bc"

    detail_scraper = ListingDetailScraper()
    details = detail_scraper.scrape(url)

    for key, value in details.items():
        print(f"{key}: {value}")


if __name__ == "__main__":
    main()