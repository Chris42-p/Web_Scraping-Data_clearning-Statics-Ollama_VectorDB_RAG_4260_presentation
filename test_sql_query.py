import sqlite3

conn = sqlite3.connect("real_estate.db")
cursor = conn.cursor()

cursor.execute("SELECT COUNT(*) FROM rew_listings")
count = cursor.fetchone()[0]

print(f"Total records in rew_listings: {count}")

cursor.execute("""
    SELECT neighbourhood, AVG(price), COUNT(*)
    FROM rew_listings
    WHERE price IS NOT NULL
    GROUP BY neighbourhood
    ORDER BY AVG(price) DESC
""")

rows = cursor.fetchall()

for row in rows:
    print(row)

conn.close()