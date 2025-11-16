import sqlite3
import requests
import time

DATABASE = 'films.db'
OMDB_API_KEY = '4e9616c3'
OMDB_BASE_URL = 'http://www.omdbapi.com/'

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
        response = requests.get(OMDB_BASE_URL, params=params)
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
        print(f"Error fetching data: {e}")
        return None

def update_rt_score(film_id, rt_score):
    """Update the Rotten Tomatoes score in the database"""
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()

    cursor.execute('UPDATE films SET rotten_tomatoes = ? WHERE id = ?', (rt_score, film_id))
    conn.commit()
    conn.close()

def main():
    print("Updating all Rotten Tomatoes scores from OMDb...")
    films = get_all_films()

    total = len(films)
    print(f"Found {total} films in database\n")

    updated = 0
    unchanged = 0
    not_found = 0
    cleared = 0

    for i, (film_id, title, year, current_rt) in enumerate(films, 1):
        print(f"[{i}/{total}] Checking: {title} ({year or 'unknown'})...")

        rt_score = fetch_rt_score_from_omdb(title, year)

        if rt_score:
            if rt_score != current_rt:
                update_rt_score(film_id, rt_score)
                print(f"  ✓ Updated: {current_rt or 'None'} -> {rt_score}")
                updated += 1
            else:
                print(f"  - Already correct: {rt_score}")
                unchanged += 1
        else:
            if current_rt:
                # Clear the existing RT score since OMDb doesn't have one
                update_rt_score(film_id, None)
                print(f"  ⚠ Cleared (not found in OMDb): {current_rt} -> None")
                cleared += 1
            else:
                print(f"  ✗ Not found (no RT score available)")
                not_found += 1

        # Rate limiting: 1 request per second to be safe
        if i < total:
            time.sleep(1)

    print(f"\n{'='*50}")
    print(f"Summary:")
    print(f"  Total films processed: {total}")
    print(f"  Updated with new scores: {updated}")
    print(f"  Already correct: {unchanged}")
    print(f"  Cleared (not in OMDb): {cleared}")
    print(f"  Not found: {not_found}")
    print(f"{'='*50}")

if __name__ == '__main__':
    main()
