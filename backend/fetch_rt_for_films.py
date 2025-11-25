#!/usr/bin/env python3
"""
Script to fetch RT scores for specific films by title.
Usage: python fetch_rt_for_films.py "Film Title 1" "Film Title 2"
"""

import sqlite3
import requests
import os
import sys

DATABASE = 'films.db'
OMDB_API_KEY = os.getenv('OMDB_API_KEY', '4e9616c3')
OMDB_BASE_URL = 'http://www.omdbapi.com/'

def fetch_rt_score_from_omdb(title, year=None):
    """Fetch Rotten Tomatoes score from OMDb API"""
    # Handle titles in "Last, First" format
    search_title = title
    if ',' in title:
        parts = title.split(',', 1)
        if len(parts) == 2:
            search_title = f"{parts[1].strip()} {parts[0].strip()}"
    
    params = {
        'apikey': OMDB_API_KEY,
        't': search_title,
        'type': 'movie'
    }
    
    if year:
        params['y'] = year
    
    try:
        response = requests.get(OMDB_BASE_URL, params=params, timeout=5)
        response.raise_for_status()
        data = response.json()
        
        if data.get('Response') == 'True':
            ratings = data.get('Ratings', [])
            for rating in ratings:
                if rating.get('Source') == 'Rotten Tomatoes':
                    rt_value = rating.get('Value', '')
                    if rt_value:
                        if '%' not in rt_value:
                            rt_value = f"{rt_value}%"
                        return rt_value
        return None
    except Exception as e:
        print(f"Error fetching RT score: {e}")
        return None

def update_films_by_title(titles):
    """Update RT scores for films matching the given titles"""
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    
    updated_count = 0
    not_found = []
    
    for title in titles:
        # Try exact match first
        cursor.execute('SELECT id, title, release_year, rotten_tomatoes FROM films WHERE title = ?', (title,))
        film = cursor.fetchone()
        
        if not film:
            # Try case-insensitive
            cursor.execute('SELECT id, title, release_year, rotten_tomatoes FROM films WHERE LOWER(title) = LOWER(?)', (title,))
            film = cursor.fetchone()
        
        if film:
            film_id, db_title, release_year, current_rt = film
            print(f"\n📽 {db_title} (ID: {film_id})")
            print(f"   Release year: {release_year}")
            print(f"   Current RT: {current_rt or 'None'}")
            
            if not current_rt:
                print(f"   Fetching RT score from OMDb...")
                rt_score = fetch_rt_score_from_omdb(db_title, release_year)
                if rt_score:
                    cursor.execute('UPDATE films SET rotten_tomatoes = ? WHERE id = ?', (rt_score, film_id))
                    conn.commit()
                    print(f"   ✅ Updated: {rt_score}")
                    updated_count += 1
                else:
                    print(f"   ⚠️  Could not find RT score on OMDb")
            else:
                print(f"   ℹ️  Already has RT score, skipping")
        else:
            print(f"\n⚠️  '{title}' not found in database")
            not_found.append(title)
    
    conn.close()
    
    print(f"\n{'='*50}")
    print(f"✅ Updated {updated_count} film(s)")
    if not_found:
        print(f"⚠️  {len(not_found)} film(s) not found: {', '.join(not_found)}")
    
    return updated_count

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("Usage: python fetch_rt_for_films.py \"Film Title 1\" \"Film Title 2\" ...")
        print("\nExample:")
        print('  python fetch_rt_for_films.py "Being Eddie" "Wicked for Good"')
        sys.exit(1)
    
    titles = sys.argv[1:]
    print(f"Fetching RT scores for {len(titles)} film(s)...")
    update_films_by_title(titles)

