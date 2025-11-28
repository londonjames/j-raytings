#!/usr/bin/env python3
"""
Extract RT hyperlinks from Google Sheets HTML export and restore them to database
"""
import sqlite3
import re
from bs4 import BeautifulSoup
from datetime import datetime
import sys
import os

# Find the HTML file
html_files = [f for f in os.listdir('.') if f.endswith('.html')]

if not html_files:
    print("❌ No HTML file found in current directory")
    print("\nPlease download your Google Sheet as HTML:")
    print("  1. File → Download → Web Page (.html, zipped)")
    print("  2. Unzip the file")
    print("  3. Move the .html file to this directory")
    sys.exit(1)

html_file = html_files[0]
print(f"Found HTML file: {html_file}")

# Parse HTML
print("Parsing HTML...")
with open(html_file, 'r', encoding='utf-8') as f:
    soup = BeautifulSoup(f.read(), 'html.parser')

# Find all table rows
rows = soup.find_all('tr')
print(f"Found {len(rows)} rows in HTML")

# Extract hyperlinks from Film column
rt_links = {}
rt_link_count = 0

for row_idx, row in enumerate(rows):
    cells = row.find_all('td')

    if len(cells) < 10:  # Need at least 10 columns (Film Year is column 10)
        continue

    # Column indices (0-based)
    # Film = column 3 (4th column)
    # Film Year = column 9 (10th column)

    film_cell = cells[3] if len(cells) > 3 else None
    year_cell = cells[9] if len(cells) > 9 else None

    if not film_cell or not year_cell:
        continue

    # Get film title
    film_title = film_cell.get_text(strip=True)

    # Get year
    try:
        year = int(year_cell.get_text(strip=True))
    except (ValueError, AttributeError):
        year = None

    if not film_title:
        continue

    # Check if film cell has a hyperlink
    link_tag = film_cell.find('a')
    if link_tag and link_tag.get('href'):
        rt_link = link_tag.get('href')

        # Only process Rotten Tomatoes links
        if 'rottentomatoes.com' in rt_link:
            key = (film_title, year)
            rt_links[key] = rt_link
            rt_link_count += 1

            if rt_link_count <= 10:
                print(f"  {film_title} ({year}) -> {rt_link}")

print(f"\n✓ Extracted {len(rt_links)} RT hyperlinks from HTML")

# Now restore to database
conn = sqlite3.connect('films.db')
cursor = conn.cursor()

# Get all films from database
cursor.execute("SELECT id, title, release_year, rt_link FROM films")
db_films = cursor.fetchall()

updated = 0
already_correct = 0
not_in_html = 0

log_file = f'restore_rt_links_from_html_{datetime.now().strftime("%Y%m%d_%H%M%S")}.txt'

with open(log_file, 'w', encoding='utf-8') as f:
    f.write("=" * 100 + "\n")
    f.write("RESTORING RT LINKS FROM GOOGLE SHEETS HTML\n")
    f.write("=" * 100 + "\n\n")

    for film_id, title, year, current_rt_link in db_films:
        key = (title, year)

        if key in rt_links:
            html_link = rt_links[key]

            if current_rt_link != html_link:
                # Update database with original link from Google Sheets
                cursor.execute("""
                    UPDATE films
                    SET rt_link = ?
                    WHERE id = ?
                """, (html_link, film_id))

                f.write(f"{title} ({year})\n")
                f.write(f"  OLD: {current_rt_link}\n")
                f.write(f"  NEW: {html_link}\n\n")

                updated += 1
            else:
                already_correct += 1
        else:
            not_in_html += 1

conn.commit()
conn.close()

print("\n" + "=" * 100)
print("RESTORATION COMPLETE")
print("=" * 100)
print(f"RT links found in Google Sheets HTML: {len(rt_links)}")
print(f"Links UPDATED (were wrong): {updated}")
print(f"Links already correct: {already_correct}")
print(f"Films in DB but no link in HTML: {not_in_html}")
print(f"\nLog saved to: {log_file}")
print("=" * 100)

if updated > 0:
    print(f"\n✅ Successfully restored {updated} RT links from your original Google Sheet!")
