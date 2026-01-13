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


# TV Genre mapping (TMDB uses different IDs for TV)
TV_GENRE_MAP = {
    10759: 'Action & Adventure',
    16: 'Animation',
    35: 'Comedy',
    80: 'Crime',
    99: 'Documentary',
    18: 'Drama',
    10751: 'Family',
    10762: 'Kids',
    9648: 'Mystery',
    10763: 'News',
    10764: 'Reality',
    10765: 'Sci-Fi & Fantasy',
    10766: 'Soap',
    10767: 'Talk',
    10768: 'War & Politics',
    37: 'Western'
}


def search_tv_show(title, year=None):
    """Search for a TV show on TMDB"""
    if not TMDB_API_KEY:
        print("Warning: TMDB_API_KEY not set")
        return None

    params = {
        'api_key': TMDB_API_KEY,
        'query': title
    }

    if year:
        params['first_air_date_year'] = year

    try:
        response = requests.get(f'{TMDB_BASE_URL}/search/tv', params=params)
        response.raise_for_status()
        data = response.json()

        if data['results']:
            # Return the first result
            show = data['results'][0]

            # Convert genre IDs to genre names
            genre_ids = show.get('genre_ids', [])
            genres = [TV_GENRE_MAP.get(gid) for gid in genre_ids if gid in TV_GENRE_MAP]

            return {
                'tmdb_id': show['id'],
                'title': show['name'],
                'poster_path': show.get('poster_path'),
                'poster_url': f"{TMDB_IMAGE_BASE_URL}{show['poster_path']}" if show.get('poster_path') else None,
                'backdrop_path': show.get('backdrop_path'),
                'overview': show.get('overview'),
                'first_air_date': show.get('first_air_date'),
                'genres': ', '.join(genres) if genres else None
            }
    except requests.exceptions.RequestException as e:
        print(f"Error searching TMDB for TV show '{title}': {e}")

    return None


def get_tv_show_details(tmdb_id):
    """Get detailed information about a TV show including seasons, episodes, and external IDs"""
    if not TMDB_API_KEY:
        return None

    try:
        # Get show details
        response = requests.get(
            f'{TMDB_BASE_URL}/tv/{tmdb_id}',
            params={'api_key': TMDB_API_KEY}
        )
        response.raise_for_status()
        data = response.json()

        # Get external IDs (for IMDB ID)
        ext_response = requests.get(
            f'{TMDB_BASE_URL}/tv/{tmdb_id}/external_ids',
            params={'api_key': TMDB_API_KEY}
        )
        ext_data = ext_response.json() if ext_response.status_code == 200 else {}

        # Calculate total episodes
        total_episodes = sum(
            season.get('episode_count', 0)
            for season in data.get('seasons', [])
            if season.get('season_number', 0) > 0  # Exclude specials (season 0)
        )

        # Get genres
        genres = [g['name'] for g in data.get('genres', [])]

        # Determine if show is ongoing
        status = data.get('status', '')
        is_ongoing = status in ['Returning Series', 'In Production']

        # Extract years
        first_air_date = data.get('first_air_date', '')
        last_air_date = data.get('last_air_date', '')
        start_year = int(first_air_date[:4]) if first_air_date else None
        end_year = None if is_ongoing else (int(last_air_date[:4]) if last_air_date else None)

        return {
            'title': data.get('name'),
            'start_year': start_year,
            'end_year': end_year,
            'is_ongoing': is_ongoing,
            'seasons': data.get('number_of_seasons'),
            'episodes': total_episodes or data.get('number_of_episodes'),
            'genres': ', '.join(genres) if genres else None,
            'overview': data.get('overview'),
            'poster_url': f"{TMDB_IMAGE_BASE_URL}{data.get('poster_path')}" if data.get('poster_path') else None,
            'imdb_id': ext_data.get('imdb_id'),
            'status': status
        }
    except requests.exceptions.RequestException as e:
        print(f"Error getting TV show details for ID {tmdb_id}: {e}")

    return None


def get_tv_poster_url(title, year=None):
    """Get just the poster URL for a TV show"""
    result = search_tv_show(title, year)
    return result['poster_url'] if result else None
