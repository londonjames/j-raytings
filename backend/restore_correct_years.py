#!/usr/bin/env python3
"""
Restore correct release years from Google Sheets HTML export
"""
import sqlite3
from bs4 import BeautifulSoup

html_file = "all films.html"

print("Parsing HTML to extract correct release years...")
with open(html_file, 'r', encoding='utf-8') as f:
    soup = BeautifulSoup(f.read(), 'html.parser')

rows = soup.find_all('tr')
print(f"Found {len(rows)} rows in HTML")

# Extract film data from HTML
films_from_html = {}

for row_idx, row in enumerate(rows):
    cells = row.find_all('td')

    if len(cells) < 10:
        continue

    # Column indices (0-based)
    # Film = column 3 (4th column)
    # Film Year = column 9 (10th column)

    film_cell = cells[3] if len(cells) > 3 else None
    year_cell = cells[9] if len(cells) > 9 else None

    if not film_cell or not year_cell:
        continue

    title = film_cell.get_text(strip=True)

    try:
        year = int(year_cell.get_text(strip=True))
    except (ValueError, AttributeError):
        continue

    if title and year:
        films_from_html[title] = year

print(f"Extracted {len(films_from_html)} films with years from Google Sheets")

# Now update the database
conn = sqlite3.connect('films.db')
cursor = conn.cursor()

# Get all films from database
cursor.execute("SELECT id, title, release_year FROM films")
all_films = cursor.fetchall()

print("\n" + "=" * 100)
print("RESTORING CORRECT RELEASE YEARS")
print("=" * 100)

updated = 0
not_found = 0

for film_id, title, db_year in all_films:
    if title in films_from_html:
        correct_year = films_from_html[title]

        if db_year != correct_year:
            print(f"Updating {title}: {db_year} → {correct_year}")
            cursor.execute("UPDATE films SET release_year = ? WHERE id = ?", (correct_year, film_id))
            updated += 1
    else:
        # Check if this film has a suspicious year
        if db_year and db_year > 2025:
            not_found += 1

conn.commit()
conn.close()

print("\n" + "=" * 100)
print(f"Updated {updated} films with correct release years")
print(f"{not_found} films not found in Google Sheets (may need manual review)")
print("=" * 100)
