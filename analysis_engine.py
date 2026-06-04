import sqlite3


class AnalysisEngine:

    def __init__(self):
        self.conn = sqlite3.connect("real_estate.db")
        self.cursor = self.conn.cursor()

    def average_price_by_neighbourhood(self):

        self.cursor.execute("""
            SELECT
                neighbourhood,
                ROUND(AVG(price), 0) AS avg_price,
                COUNT(*) AS listings
            FROM rew_listings
            WHERE price IS NOT NULL
            GROUP BY neighbourhood
            ORDER BY avg_price DESC
        """)

        rows = self.cursor.fetchall()

        print("\n=== Average Price By Neighbourhood ===\n")

        for row in rows:
            neighbourhood, avg_price, listings = row

            print(
                f"{neighbourhood:<25}"
                f"${avg_price:,.0f}   "
                f"({listings} listings)"
            )

    def average_price_per_sqft(self):

        self.cursor.execute("""
            SELECT
                neighbourhood,
                ROUND(AVG(price * 1.0 / square_feet),2)
            FROM rew_listings
            WHERE
                price IS NOT NULL
                AND square_feet IS NOT NULL
                AND square_feet > 0
            GROUP BY neighbourhood
            ORDER BY AVG(price * 1.0 / square_feet) DESC
        """)

        rows = self.cursor.fetchall()

        print("\n=== Average Price Per SqFt ===\n")

        for row in rows:
            print(row)

    def property_type_distribution(self):

        self.cursor.execute("""
            SELECT
                property_type,
                COUNT(*)
            FROM rew_listings
            GROUP BY property_type
            ORDER BY COUNT(*) DESC
        """)

        rows = self.cursor.fetchall()

        print("\n=== Property Type Distribution ===\n")

        for row in rows:
            print(row)

    def run(self):

        self.average_price_by_neighbourhood()

        self.average_price_per_sqft()

        self.property_type_distribution()

        self.average_rooms_by_neighbourhood()

        self.top_5_most_expensive()

        self.conn.close()
    
    def average_rooms_by_neighbourhood(self):

        self.cursor.execute("""
            SELECT
                neighbourhood,
                ROUND(AVG(bedrooms), 1) AS avg_bedrooms,
                ROUND(AVG(bathrooms), 1) AS avg_bathrooms,
                COUNT(*) AS listings
            FROM rew_listings
            WHERE bedrooms IS NOT NULL
            GROUP BY neighbourhood
            ORDER BY avg_bedrooms DESC
        """)

        rows = self.cursor.fetchall()

        print("\n=== Average Bedrooms/Bathrooms By Neighbourhood ===\n")

        for row in rows:
            neighbourhood, avg_bedrooms, avg_bathrooms, listings = row

            print(
                f"{neighbourhood:<25}"
                f"Beds: {avg_bedrooms:<4} "
                f"Baths: {avg_bathrooms:<4} "
                f"({listings} listings)"
            )

    def top_5_most_expensive(self):

        self.cursor.execute("""
            SELECT
                price,
                address,
                property_type,
                bedrooms,
                bathrooms,
                square_feet
            FROM rew_listings
            WHERE price IS NOT NULL
            ORDER BY price DESC
            LIMIT 5
        """)

        rows = self.cursor.fetchall()

        print("\n=== Top 5 Most Expensive Listings ===\n")

        for row in rows:
            price, address, property_type, bedrooms, bathrooms, square_feet = row

            print(
                f"${price:,.0f} | "
                f"{address} | "
                f"{property_type} | "
                f"{bedrooms} bd / {bathrooms} ba | "
                f"{square_feet} sqft"
            )


if __name__ == "__main__":
    AnalysisEngine().run()