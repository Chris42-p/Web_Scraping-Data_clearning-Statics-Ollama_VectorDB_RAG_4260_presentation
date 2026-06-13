"""
CSV Storage Module

Responsible for saving scraped listings into a CSV file.

Current implementation:
    Website -> ListingObject -> CSV

Future improvements:
    CSV -> SQLite
    CSV -> ChromaDB
    CSV -> Analytics Pipeline
"""

import csv
from pathlib import Path


class ListingCSVStorage:
    """
    Handles CSV persistence for scraped listings.
    """

    def __init__(self, output_path="scraped_data/rew_listings.csv"):
        """
        Create storage location if it does not exist.
        """
        self.output_path = Path(output_path)
        self.output_path.parent.mkdir(
            parents=True,
            exist_ok=True
        )

    def save(self, listings):
        """
        Save a collection of ListingObjects to CSV.

        Parameters:
            listings (list):
                List of ListingObject instances.
        """

        if not listings:
            print("No listings to save.")
            return

        rows = [
            listing.to_json()
            for listing in listings
        ]

        fieldnames = rows[0].keys()

        with open(
            self.output_path,
            mode="w",
            newline="",
            encoding="utf-8"
        ) as file:

            writer = csv.DictWriter(
                file,
                fieldnames=fieldnames
            )

            writer.writeheader()
            writer.writerows(rows)

        print(
            f"Saved {len(rows)} listings to {self.output_path}"
        )