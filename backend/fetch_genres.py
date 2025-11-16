#!/usr/bin/env python3
"""
Fetch and populate genre data for all films from TMDB
"""

import sqlite3
import time
from tmdb_service import search_movie

DATABASE = 'films.db'

def fetch_genres():
    """Fetch genres for all films from TMDB"""
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    # Get all films that don't have genres yet
    cursor.execute('''
        SELECT id, title, release_year
        FROM films
        WHERE genres IS NULL OR genres = ''
        ORDER BY id
    ''')

    films = cursor.fetchall()
    total = len(films)

    print(f"\n🎬 Found {total} films without genre data")
    print(f"⏱️  Estimated time: ~{int(total * 0.25 / 60)} minutes\n")

    success_count = 0
    fail_count = 0

    for i, film in enumerate(films, 1):
        film_id = film['id']
        title = film['title']
        year = film['release_year']

        print(f"[{i}/{total}] Fetching genres for: {title} ({year})...", end=' ')

        try:
            # Search for movie on TMDB
            result = search_movie(title, year)

            if result and result.get('genres'):
                genres = result['genres']

                # Update database with genres
                cursor.execute('''
                    UPDATE films
                    SET genres = ?
                    WHERE id = ?
                ''', (genres, film_id))

                conn.commit()
                print(f"✅ {genres}")
                success_count += 1
            else:
                print(f"⚠️  No genres found")
                fail_count += 1

        except Exception as e:
            print(f"❌ Error: {e}")
            fail_count += 1

        # Rate limiting - TMDB allows 40 requests per 10 seconds
        if i < total:
            time.sleep(0.25)

        # Progress update every 50 films
        if i % 50 == 0:
            print(f"\n📊 Progress: {i}/{total} ({int(i/total*100)}%) - Success: {success_count}, Failed: {fail_count}\n")

    conn.close()

    print(f"\n✨ Genre fetch complete!")
    print(f"📈 Success: {success_count}")
    print(f"❌ Failed: {fail_count}")
    print(f"📊 Total: {total}")

if __name__ == '__main__':
    fetch_genres()
