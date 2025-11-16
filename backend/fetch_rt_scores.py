import sqlite3
import requests
import time
import os

DATABASE = 'films.db'
OMDB_API_KEY = '4e9616c3'
OMDB_BASE_URL = 'http://www.omdbapi.com/'

def get_films_missing_data():
    """Get all films that are missing any data"""
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()

    cursor.execute('''
        SELECT id, title, release_year, length_minutes, rotten_tomatoes
        FROM films
        WHERE rotten_tomatoes IS NULL OR rotten_tomatoes = ''
           OR release_year IS NULL OR release_year = ''
           OR length_minutes IS NULL OR length_minutes = ''
        ORDER BY id
    ''')

    films = cursor.fetchall()
    conn.close()
    return films

def fetch_data_from_omdb(title, year):
    """Fetch movie data from OMDb API"""
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
            result = {
                'rt_score': None,
                'year': None,
                'runtime': None
            }

            # Get Rotten Tomatoes score
            ratings = data.get('Ratings', [])
            for rating in ratings:
                if rating.get('Source') == 'Rotten Tomatoes':
                    result['rt_score'] = rating.get('Value')  # Returns like "85%"

            # Get year
            if data.get('Year') and data.get('Year') != 'N/A':
                result['year'] = data.get('Year')

            # Get runtime (e.g., "142 min" -> 142)
            if data.get('Runtime') and data.get('Runtime') != 'N/A':
                runtime_str = data.get('Runtime')
                # Extract number from "142 min"
                runtime_num = runtime_str.split()[0] if ' ' in runtime_str else runtime_str
                try:
                    result['runtime'] = int(runtime_num)
                except ValueError:
                    pass

            return result

        return None
    except Exception as e:
        print(f"Error fetching data: {e}")
        return None

def update_film_data(film_id, rt_score, year, runtime):
    """Update the film data in the database"""
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()

    # Build update query dynamically based on what data we have
    updates = []
    values = []

    if rt_score:
        updates.append('rotten_tomatoes = ?')
        values.append(rt_score)
    if year:
        updates.append('release_year = ?')
        values.append(year)
    if runtime:
        updates.append('length_minutes = ?')
        values.append(runtime)

    if updates:
        values.append(film_id)
        query = f"UPDATE films SET {', '.join(updates)} WHERE id = ?"
        cursor.execute(query, values)
        conn.commit()

    conn.close()

def main():
    print("Fetching missing film data from OMDb...")
    films = get_films_missing_data()

    total = len(films)
    print(f"Found {total} films missing data\n")

    if total == 0:
        print("All films already have complete data!")
        return

    updated = 0
    not_found = 0
    stats = {
        'rt_scores': 0,
        'years': 0,
        'runtimes': 0
    }

    for i, (film_id, title, year, runtime, rt_score) in enumerate(films, 1):
        print(f"[{i}/{total}] Fetching data for: {title} ({year or 'unknown'})...")

        data = fetch_data_from_omdb(title, year)

        if data:
            # Track what we're updating
            updates = []
            if data['rt_score']:
                updates.append(f"RT: {data['rt_score']}")
                stats['rt_scores'] += 1
            if data['year'] and not year:
                updates.append(f"Year: {data['year']}")
                stats['years'] += 1
            if data['runtime'] and not runtime:
                updates.append(f"Runtime: {data['runtime']} min")
                stats['runtimes'] += 1

            if updates:
                update_film_data(film_id, data['rt_score'], data['year'], data['runtime'])
                print(f"  ✓ Updated: {', '.join(updates)}")
                updated += 1
            else:
                print(f"  - No new data found")
        else:
            print(f"  ✗ Not found")
            not_found += 1

        # Rate limiting: 1 request per second to be safe (free tier allows more)
        if i < total:
            time.sleep(1)

    print(f"\n{'='*50}")
    print(f"Summary:")
    print(f"  Total films processed: {total}")
    print(f"  Successfully updated: {updated}")
    print(f"  Not found: {not_found}")
    print(f"\nData updated:")
    print(f"  RT scores added: {stats['rt_scores']}")
    print(f"  Years added: {stats['years']}")
    print(f"  Runtimes added: {stats['runtimes']}")
    print(f"{'='*50}")

if __name__ == '__main__':
    main()
