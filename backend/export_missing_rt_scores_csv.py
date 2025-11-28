import sqlite3
import csv
from datetime import datetime

db_path = 'films.db'
output_file = f'missing_rt_scores_{datetime.now().strftime("%Y%m%d_%H%M%S")}.csv'

conn = sqlite3.connect(db_path)
cursor = conn.cursor()

# Get all films missing RT scores
cursor.execute("""
    SELECT title, release_year, score, rt_link
    FROM films
    WHERE rotten_tomatoes IS NULL OR rotten_tomatoes = ''
    ORDER BY release_year DESC, title ASC
""")

missing_films = cursor.fetchall()
conn.close()

# Write to CSV
with open(output_file, 'w', newline='', encoding='utf-8') as f:
    writer = csv.writer(f)

    # Header row
    writer.writerow(['Film Title', 'Year', 'Your Rating', 'RT Link', 'RT Score (Fill In)'])

    # Data rows
    for title, year, score, rt_link in missing_films:
        writer.writerow([
            title,
            year if year else '',
            score if score else '',
            rt_link if rt_link else '',
            ''  # Empty column for RT score to fill in
        ])

print(f"✅ CSV file created: {output_file}")
print(f"Total films: {len(missing_films)}")
print(f"\nColumns:")
print("  1. Film Title")
print("  2. Year")
print("  3. Your Rating")
print("  4. RT Link")
print("  5. RT Score (Fill In) - Leave this column empty for now")
