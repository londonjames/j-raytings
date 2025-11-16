import sqlite3
import requests
import time
from concurrent.futures import ThreadPoolExecutor, as_completed

DATABASE = 'films.db'
OMDB_API_KEY = '4e9616c3'
OMDB_BASE_URL = 'http://www.omdbapi.com/'
MAX_WORKERS = 10  # Process 10 films at a time

def get_all_films():
    """Get all films from the database"""
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()

    cursor.execute('''
        SELECT id, title, release_year, rotten_tomatoes
        FROM films
        ORDER BY id
    ''')

    films = cursor.fetchall()
    conn.close()
    return films

def fetch_rt_score_from_omdb(title, year):
    """Fetch Rotten Tomatoes score from OMDb API"""
    # Handle titles in "Last, First" format (e.g., "Fugitive, The" -> "The Fugitive")
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

    # Only include year if we have it
    if year:
        params['y'] = year

    try:
        response = requests.get(OMDB_BASE_URL, params=params, timeout=10)
        response.raise_for_status()
        data = response.json()

        if data.get('Response') == 'True':
            # Get Rotten Tomatoes score
            ratings = data.get('Ratings', [])
            for rating in ratings:
                if rating.get('Source') == 'Rotten Tomatoes':
                    return rating.get('Value')  # Returns like "85%"

        return None
    except Exception as e:
        print(f"Error fetching {title}: {e}")
        return None

def update_rt_score(film_id, rt_score):
    """Update the Rotten Tomatoes score in the database"""
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()

    cursor.execute('UPDATE films SET rotten_tomatoes = ? WHERE id = ?', (rt_score, film_id))
    conn.commit()
    conn.close()

def process_film(film_data):
    """Process a single film - fetch and update if needed"""
    film_id, title, year, current_rt = film_data

    rt_score = fetch_rt_score_from_omdb(title, year)

    result = {
        'title': title,
        'year': year,
        'current': current_rt,
        'new': rt_score,
        'action': None
    }

    if rt_score:
        if rt_score != current_rt:
            update_rt_score(film_id, rt_score)
            result['action'] = 'updated'
        else:
            result['action'] = 'unchanged'
    else:
        if current_rt:
            update_rt_score(film_id, None)
            result['action'] = 'cleared'
        else:
            result['action'] = 'not_found'

    return result

def main():
    print("Updating all Rotten Tomatoes scores from OMDb (parallel processing)...")
    print(f"Using {MAX_WORKERS} parallel workers\n")

    films = get_all_films()
    total = len(films)
    print(f"Found {total} films in database\n")

    stats = {
        'updated': 0,
        'unchanged': 0,
        'cleared': 0,
        'not_found': 0
    }

    processed = 0

    # Process films in parallel
    with ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
        # Submit all tasks
        future_to_film = {executor.submit(process_film, film): film for film in films}

        # Process results as they complete
        for future in as_completed(future_to_film):
            try:
                result = future.result()
                processed += 1

                # Print progress
                status_char = {
                    'updated': '✓',
                    'unchanged': '-',
                    'cleared': '⚠',
                    'not_found': '✗'
                }[result['action']]

                print(f"[{processed}/{total}] {status_char} {result['title']} ({result['year'] or 'unknown'}): {result['current'] or 'None'} -> {result['new'] or 'None'}")

                stats[result['action']] += 1

            except Exception as e:
                print(f"Error processing film: {e}")

    print(f"\n{'='*50}")
    print(f"Summary:")
    print(f"  Total films processed: {total}")
    print(f"  Updated with new scores: {stats['updated']}")
    print(f"  Already correct: {stats['unchanged']}")
    print(f"  Cleared (not in OMDb): {stats['cleared']}")
    print(f"  Not found: {stats['not_found']}")
    print(f"{'='*50}")

if __name__ == '__main__':
    main()
