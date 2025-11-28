#!/usr/bin/env python3
"""
Fix films with obviously wrong release years by fetching correct data from TMDB
"""
import sqlite3
import os
from tmdb_service import search_movie, get_movie_details

conn = sqlite3.connect('films.db')
cursor = conn.cursor()

# Find films with suspicious years (watched Pre-2006 but release year > 2006)
cursor.execute("""
    SELECT id, title, release_year, year_watched
    FROM films
    WHERE year_watched = 'Pre-2006'
    AND release_year > 2006
    ORDER BY title
""")

suspicious_films = cursor.fetchall()

print("=" * 100)
print(f"FIXING {len(suspicious_films)} FILMS WITH OBVIOUSLY WRONG YEARS")
print("=" * 100)
print()

updated = 0
not_found = 0

for film_id, title, wrong_year, year_watched in suspicious_films:
    print(f"{title} (currently shows {wrong_year}, watched Pre-2006)")

    # Search TMDB for the correct match
    # For Pre-2006 films, we want matches from before 2006
    try:
        # Search without year filter first to see all matches
        movie_data = search_movie(title, year=None)

        if movie_data:
            tmdb_id = movie_data.get('tmdb_id')
            if tmdb_id:
                details = get_movie_details(tmdb_id)
                if details and details.get('release_date'):
                    correct_year = int(details['release_date'][:4])

                    # Only update if the year is before 2006 (since film was watched Pre-2006)
                    if correct_year < 2006:
                        print(f"  ✓ Updating to {correct_year}")
                        cursor.execute("UPDATE films SET release_year = ? WHERE id = ?",
                                     (correct_year, film_id))
                        updated += 1
                    else:
                        print(f"  ⚠ TMDB suggests {correct_year}, but film was watched Pre-2006")
                        print(f"     Leaving as {wrong_year} for manual review")
                else:
                    print(f"  ✗ Could not get release date from TMDB")
                    not_found += 1
        else:
            print(f"  ✗ Not found in TMDB")
            not_found += 1
    except Exception as e:
        print(f"  ✗ Error: {e}")
        not_found += 1

    print()

conn.commit()
conn.close()

print("=" * 100)
print(f"Updated: {updated}")
print(f"Not found/Error: {not_found}")
print("=" * 100)
