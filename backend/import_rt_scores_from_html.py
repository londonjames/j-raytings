#!/usr/bin/env python3
"""
Extract RT scores from Google Sheets HTML export and import them to database
"""
import sqlite3
import re
from bs4 import BeautifulSoup
from datetime import datetime

html_file = "all films.html"

print("Parsing HTML to extract RT scores...")
with open(html_file, 'r', encoding='utf-8') as f:
    soup = BeautifulSoup(f.read(), 'html.parser')

# Find all table rows
rows = soup.find_all('tr')
print(f"Found {len(rows)} rows in HTML")

# Extract RT scores from Rotten Tomatoes column
rt_scores_to_import = []

for row_idx, row in enumerate(rows):
    cells = row.find_all('td')

    if len(cells) < 11:  # Need at least 11 columns
        continue

    # Column indices (0-based)
    # Film = column 3 (4th column)
    # Film Year = column 9 (10th column)
    # Rotten Tomatoes = column 10 (11th column)

    film_cell = cells[3] if len(cells) > 3 else None
    year_cell = cells[9] if len(cells) > 9 else None
    rt_cell = cells[10] if len(cells) > 10 else None

    if not film_cell or not year_cell or not rt_cell:
        continue

    # Get film title
    film_title = film_cell.get_text(strip=True)

    # Get year
    try:
        year = int(year_cell.get_text(strip=True))
    except (ValueError, AttributeError):
        year = None

    # Get RT score
    rt_score = rt_cell.get_text(strip=True)

    if not film_title or not rt_score:
        continue

    # Only process if RT score looks valid (percentage)
    if '%' in rt_score or rt_score.replace('.', '').replace('%', '').isdigit():
        # Ensure it has % symbol
        if '%' not in rt_score:
            rt_score = rt_score + '%'

        rt_scores_to_import.append({
            'title': film_title,
            'year': year,
            'rt_score': rt_score
        })

        if len(rt_scores_to_import) <= 10:
            print(f"  {film_title} ({year}) -> {rt_score}")

print(f"\n✓ Found {len(rt_scores_to_import)} films with RT scores in Google Sheets")

# Now import to database
conn = sqlite3.connect('films.db')
cursor = conn.cursor()

imported = 0
already_had_score = 0
not_found = 0

log_file = f'import_rt_scores_from_html_{datetime.now().strftime("%Y%m%d_%H%M%S")}.txt'

with open(log_file, 'w', encoding='utf-8') as f:
    f.write("=" * 100 + "\n")
    f.write("IMPORTING RT SCORES FROM GOOGLE SHEETS HTML\n")
    f.write("=" * 100 + "\n\n")

    for item in rt_scores_to_import:
        title = item['title']
        year = item['year']
        rt_score = item['rt_score']

        # Find film in database
        cursor.execute("""
            SELECT id, rotten_tomatoes
            FROM films
            WHERE title = ? AND release_year = ?
        """, (title, year))

        result = cursor.fetchone()

        if result:
            film_id, current_score = result

            # Only update if current score is NULL or empty
            if not current_score or current_score.strip() == '':
                cursor.execute("""
                    UPDATE films
                    SET rotten_tomatoes = ?
                    WHERE id = ?
                """, (rt_score, film_id))

                f.write(f"✓ {title} ({year}): Added {rt_score}\n")
                imported += 1
            else:
                already_had_score += 1
        else:
            f.write(f"✗ {title} ({year}): Not found in database\n")
            not_found += 1

conn.commit()
conn.close()

print("\n" + "=" * 100)
print("IMPORT COMPLETE")
print("=" * 100)
print(f"RT scores in Google Sheets: {len(rt_scores_to_import)}")
print(f"Scores IMPORTED (were missing): {imported}")
print(f"Already had scores: {already_had_score}")
print(f"Not found in database: {not_found}")
print(f"\nLog saved to: {log_file}")
print("=" * 100)

if imported > 0:
    print(f"\n✅ Successfully imported {imported} RT scores from your Google Sheet!")
