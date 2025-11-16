#!/usr/bin/env python3
"""
Fetch movie posters from TMDB for all films in the database.

Usage:
    1. Set your TMDB API key: export TMDB_API_KEY="your_key_here"
    2. Run: python fetch_posters.py

Optional arguments:
    --limit N : Only fetch posters for first N films (for testing)
    --missing-only : Only fetch posters for films without posters
"""

import sqlite3
import sys
import os
from tmdb_service import batch_fetch_posters

DATABASE = 'films.db'

def fetch_all_posters(limit=None, missing_only=False):
    """Fetch posters for all films in database"""

    # Check for API key
    if not os.getenv('TMDB_API_KEY'):
        print("❌ Error: TMDB_API_KEY environment variable not set!")
        print("\nTo get an API key:")
        print("1. Go to https://www.themoviedb.org/")
        print("2. Create a free account")
        print("3. Go to Settings → API → Request an API Key")
        print("4. Choose 'Developer' and fill out the form")
        print("\nThen run:")
        print("  export TMDB_API_KEY='your_api_key_here'")
        print("  python fetch_posters.py")
        sys.exit(1)

    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    # Build query
    query = "SELECT id, title, release_year, poster_url FROM films"
    if missing_only:
        query += " WHERE poster_url IS NULL OR poster_url = ''"

    if limit:
        query += f" LIMIT {limit}"

    cursor.execute(query)
    films = [dict(row) for row in cursor.fetchall()]

    if not films:
        print("✅ All films already have posters!")
        conn.close()
        return

    print(f"📥 Fetching posters for {len(films)} films...")
    print(f"⏱️  This will take approximately {len(films) * 0.25 / 60:.1f} minutes")
    print()

    # Fetch posters
    results = batch_fetch_posters(films)

    # Update database
    print("\n💾 Updating database...")
    success_count = 0
    missing_count = 0

    for result in results:
        if result['poster_url']:
            cursor.execute(
                'UPDATE films SET poster_url = ? WHERE id = ?',
                (result['poster_url'], result['id'])
            )
            success_count += 1
        else:
            missing_count += 1

    conn.commit()
    conn.close()

    print(f"\n✅ Complete!")
    print(f"   {success_count} posters found and saved")
    if missing_count > 0:
        print(f"   {missing_count} films had no poster available")

if __name__ == '__main__':
    import argparse

    parser = argparse.ArgumentParser(description='Fetch movie posters from TMDB')
    parser.add_argument('--limit', type=int, help='Only fetch N films (for testing)')
    parser.add_argument('--missing-only', action='store_true', help='Only fetch missing posters')

    args = parser.parse_args()

    fetch_all_posters(limit=args.limit, missing_only=args.missing_only)
