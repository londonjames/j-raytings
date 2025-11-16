#!/usr/bin/env python3
"""
Script to fetch missing release year and duration data from TMDB
"""
import sqlite3
import time
from tmdb_service import search_movie, get_movie_details

DATABASE = 'films.db'

def get_films_missing_metadata():
    """Get all films missing release_year or length_minutes"""
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    cursor.execute('''
        SELECT id, title, release_year, length_minutes
        FROM films
        WHERE (release_year IS NULL OR release_year = '')
           OR (length_minutes IS NULL OR length_minutes = '')
        ORDER BY title
    ''')

    films = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return films

def update_film_metadata(film_id, release_year=None, length_minutes=None):
    """Update a film's metadata in the database"""
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()

    updates = []
    params = []

    if release_year is not None:
        updates.append('release_year = ?')
        params.append(release_year)

    if length_minutes is not None:
        updates.append('length_minutes = ?')
        params.append(length_minutes)

    if updates:
        params.append(film_id)
        query = f"UPDATE films SET {', '.join(updates)} WHERE id = ?"
        cursor.execute(query, params)
        conn.commit()

    conn.close()

def main():
    films = get_films_missing_metadata()
    print(f"Found {len(films)} films with missing metadata")
    print("-" * 60)

    updated_count = 0
    failed_count = 0

    for i, film in enumerate(films):
        title = film['title']
        film_id = film['id']
        missing_year = not film['release_year']
        missing_duration = not film['length_minutes']

        print(f"\n[{i+1}/{len(films)}] Processing: {title}")
        print(f"  Missing: Year={missing_year}, Duration={missing_duration}")

        # Search for the movie
        result = search_movie(title)

        if result:
            tmdb_id = result['tmdb_id']
            release_year = None
            length_minutes = None

            # Get release year from search result
            if missing_year and result.get('release_date'):
                release_year = result['release_date'][:4]  # Extract year
                print(f"  Found year: {release_year}")

            # Get duration from movie details
            if missing_duration:
                details = get_movie_details(tmdb_id)
                if details and details.get('runtime'):
                    length_minutes = details['runtime']
                    print(f"  Found duration: {length_minutes} minutes")
                time.sleep(0.25)  # Additional delay for second API call

            # Update database if we found any missing data
            if release_year or length_minutes:
                update_film_metadata(film_id, release_year, length_minutes)
                updated_count += 1
                print(f"  ✓ Updated database")
            else:
                print(f"  ✗ No metadata found on TMDB")
                failed_count += 1
        else:
            print(f"  ✗ Movie not found on TMDB")
            failed_count += 1

        # Rate limiting - TMDB allows 40 requests per 10 seconds
        if i < len(films) - 1:
            time.sleep(0.25)

        # Progress update every 50 films
        if (i + 1) % 50 == 0:
            print(f"\n--- Progress: {i+1}/{len(films)} films processed ---")
            print(f"    Updated: {updated_count}, Failed: {failed_count}")

    print("\n" + "=" * 60)
    print(f"COMPLETE!")
    print(f"Total films processed: {len(films)}")
    print(f"Successfully updated: {updated_count}")
    print(f"Failed to find: {failed_count}")
    print("=" * 60)

if __name__ == '__main__':
    main()
