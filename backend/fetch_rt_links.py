#!/usr/bin/env python3
"""
Fetch Rotten Tomatoes links for all films using TMDB API

This will:
1. Get TMDB data for each film
2. Extract the IMDB ID
3. Build Rotten Tomatoes URL (format: https://www.rottentomatoes.com/m/title)
4. Update database with RT links

Usage:
    TMDB_API_KEY='your_key' python3 fetch_rt_links.py
"""

import sqlite3
import requests
import os
import time
import re

DATABASE = 'films.db'
API_KEY = os.getenv('TMDB_API_KEY')

def slugify_title(title):
    """Convert title to Rotten Tomatoes URL slug format"""
    # Remove special characters and convert to lowercase
    slug = title.lower()
    # Remove articles at the beginning
    slug = re.sub(r'^(the|a|an)\s+', '', slug)
    # Replace spaces and special chars with underscores
    slug = re.sub(r'[^\w\s-]', '', slug)
    slug = re.sub(r'[-\s]+', '_', slug)
    return slug

def get_tmdb_movie_data(title, year):
    """Get movie data from TMDB including external IDs"""
    try:
        # Search for the movie
        search_url = 'https://api.themoviedb.org/3/search/movie'
        params = {
            'api_key': API_KEY,
            'query': title,
            'year': year
        }

        response = requests.get(search_url, params=params)
        results = response.json().get('results', [])

        if not results:
            return None

        movie_id = results[0]['id']

        # Get external IDs
        external_url = f'https://api.themoviedb.org/3/movie/{movie_id}/external_ids'
        params = {'api_key': API_KEY}

        response = requests.get(external_url, params=params)
        external_data = response.json()

        return {
            'imdb_id': external_data.get('imdb_id'),
            'title': results[0]['title'],
            'year': results[0].get('release_date', '')[:4]
        }

    except Exception as e:
        print(f"Error fetching data for {title}: {e}")
        return None

def build_rt_url(title, year, imdb_id=None):
    """Build Rotten Tomatoes URL"""
    # RT URL format: https://www.rottentomatoes.com/m/title_year (sometimes)
    slug = slugify_title(title)

    # Common RT URL patterns:
    # 1. /m/movie_title
    # 2. /m/movie_title_year
    # We'll use pattern 1 as default

    return f"https://www.rottentomatoes.com/m/{slug}"

def fetch_all_rt_links(limit=None):
    """Fetch RT links for all films"""

    if not API_KEY:
        print("❌ Error: TMDB_API_KEY not set!")
        return

    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    # Check if rt_link column exists, if not add it
    cursor.execute("PRAGMA table_info(films)")
    columns = [col[1] for col in cursor.fetchall()]

    if 'rt_link' not in columns:
        print("Adding rt_link column to database...")
        cursor.execute('ALTER TABLE films ADD COLUMN rt_link TEXT')
        conn.commit()

    # Get all films
    query = 'SELECT id, title, release_year FROM films WHERE release_year IS NOT NULL'
    if limit:
        query += f' LIMIT {limit}'

    cursor.execute(query)
    films = cursor.fetchall()

    print(f"📥 Fetching RT links for {len(films)} films...")
    print(f"⏱️  This will take approximately {len(films) * 0.3 / 60:.1f} minutes")
    print()

    success_count = 0
    failed_count = 0

    for i, film in enumerate(films, 1):
        film_id = film['id']
        title = film['title']
        year = film['release_year']

        print(f"[{i}/{len(films)}] {title} ({year})...")

        # Get TMDB data
        movie_data = get_tmdb_movie_data(title, year)

        if movie_data:
            # Build RT URL
            rt_url = build_rt_url(title, year, movie_data.get('imdb_id'))

            # Update database
            cursor.execute('UPDATE films SET rt_link = ? WHERE id = ?', (rt_url, film_id))
            print(f"  ✓ {rt_url}")
            success_count += 1
        else:
            # Try with just the title slug
            rt_url = build_rt_url(title, year)
            cursor.execute('UPDATE films SET rt_link = ? WHERE id = ?', (rt_url, film_id))
            print(f"  ~ {rt_url} (best guess)")
            failed_count += 1

        # Commit every 10 films
        if i % 10 == 0:
            conn.commit()

        # Rate limiting
        time.sleep(0.3)

    conn.commit()
    conn.close()

    print(f"\n✅ Complete!")
    print(f"   {success_count} RT links generated from TMDB data")
    print(f"   {failed_count} RT links generated as best guess")
    print(f"\nNote: Some URLs may need manual verification.")
    print(f"RT often uses different slugs than the exact title.")

if __name__ == '__main__':
    import argparse

    parser = argparse.ArgumentParser(description='Fetch Rotten Tomatoes links')
    parser.add_argument('--limit', type=int, help='Only process N films (for testing)')

    args = parser.parse_args()

    fetch_all_rt_links(limit=args.limit)
