import requests
import os
import time

TMDB_API_KEY = os.getenv('TMDB_API_KEY', '')
TMDB_BASE_URL = 'https://api.themoviedb.org/3'
TMDB_IMAGE_BASE_URL = 'https://image.tmdb.org/t/p/w500'

# TMDB Genre mapping
GENRE_MAP = {
    28: 'Action',
    12: 'Adventure',
    16: 'Animation',
    35: 'Comedy',
    80: 'Crime',
    99: 'Documentary',
    18: 'Drama',
    10751: 'Family',
    14: 'Fantasy',
    36: 'History',
    27: 'Horror',
    10402: 'Music',
    9648: 'Mystery',
    10749: 'Romance',
    878: 'Sci Fi',
    10770: 'TV Movie',
    53: 'Thriller',
    10752: 'War',
    37: 'Western'
}

def search_movie(title, year=None):
    """Search for a movie on TMDB"""
    if not TMDB_API_KEY:
        print("Warning: TMDB_API_KEY not set")
        return None

    # Handle titles in "Last, First" format (e.g., "Fugitive, The" -> "The Fugitive")
    search_title = title
    if ',' in title:
        parts = title.split(',', 1)
        if len(parts) == 2:
            search_title = f"{parts[1].strip()} {parts[0].strip()}"

    params = {
        'api_key': TMDB_API_KEY,
        'query': search_title
    }

    if year:
        params['year'] = year

    try:
        response = requests.get(f'{TMDB_BASE_URL}/search/movie', params=params)
        response.raise_for_status()
        data = response.json()

        if data['results']:
            # Return the first result
            movie = data['results'][0]

            # Convert genre IDs to genre names
            genre_ids = movie.get('genre_ids', [])
            genres = [GENRE_MAP.get(gid) for gid in genre_ids if gid in GENRE_MAP]

            return {
                'tmdb_id': movie['id'],
                'title': movie['title'],
                'poster_path': movie.get('poster_path'),
                'poster_url': f"{TMDB_IMAGE_BASE_URL}{movie['poster_path']}" if movie.get('poster_path') else None,
                'backdrop_path': movie.get('backdrop_path'),
                'overview': movie.get('overview'),
                'release_date': movie.get('release_date'),
                'genres': ', '.join(genres) if genres else None
            }
    except requests.exceptions.RequestException as e:
        print(f"Error searching TMDB for '{title}': {e}")

    return None

def get_movie_details(tmdb_id):
    """Get detailed information about a movie including runtime"""
    if not TMDB_API_KEY:
        return None

    try:
        response = requests.get(
            f'{TMDB_BASE_URL}/movie/{tmdb_id}',
            params={'api_key': TMDB_API_KEY}
        )
        response.raise_for_status()
        data = response.json()

        return {
            'runtime': data.get('runtime'),  # in minutes
            'release_date': data.get('release_date'),
            'title': data.get('title')
        }
    except requests.exceptions.RequestException as e:
        print(f"Error getting movie details for ID {tmdb_id}: {e}")

    return None

def get_poster_url(title, year=None):
    """Get just the poster URL for a movie"""
    result = search_movie(title, year)
    return result['poster_url'] if result else None

def batch_fetch_posters(films, delay=0.25):
    """Fetch posters for multiple films with rate limiting"""
    results = []

    for i, film in enumerate(films):
        title = film.get('title')
        year = film.get('release_year')
        film_id = film.get('id')

        print(f"Fetching poster for '{title}' ({i+1}/{len(films)})...")

        poster_url = get_poster_url(title, year)

        results.append({
            'id': film_id,
            'title': title,
            'poster_url': poster_url
        })

        # Rate limiting - TMDB allows 40 requests per 10 seconds
        if i < len(films) - 1:
            time.sleep(delay)

    return results
