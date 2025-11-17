from flask import Flask, request, jsonify
from flask_cors import CORS
import sqlite3
import os
from tmdb_service import search_movie, get_movie_details
import re
from urllib.parse import urlparse

app = Flask(__name__)
CORS(app)

DATABASE = 'films.db'

# Detect if we should use PostgreSQL or SQLite
DATABASE_URL = os.getenv('DATABASE_URL')
USE_POSTGRES = DATABASE_URL is not None

if USE_POSTGRES:
    import psycopg2
    from psycopg2.extras import RealDictCursor

    # Parse DATABASE_URL for psycopg2
    result = urlparse(DATABASE_URL)
    DB_CONFIG = {
        'dbname': result.path[1:],
        'user': result.username,
        'password': result.password,
        'host': result.hostname,
        'port': result.port
    }

def get_db():
    """Get database connection (PostgreSQL or SQLite based on environment)"""
    if USE_POSTGRES:
        conn = psycopg2.connect(**DB_CONFIG)
        return conn
    else:
        conn = sqlite3.connect(DATABASE)
        conn.row_factory = sqlite3.Row
        return conn

def init_db():
    """Initialize the database"""
    conn = get_db()
    cursor = conn.cursor()

    if USE_POSTGRES:
        # PostgreSQL syntax
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS films (
                id SERIAL PRIMARY KEY,
                order_number INTEGER,
                date_seen TEXT,
                title TEXT NOT NULL,
                letter_rating TEXT,
                score INTEGER,
                year_watched TEXT,
                location TEXT,
                format TEXT,
                release_year INTEGER,
                rotten_tomatoes TEXT,
                length_minutes INTEGER,
                rt_per_minute TEXT,
                genres TEXT,
                poster_url TEXT,
                rt_link TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
    else:
        # SQLite syntax
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS films (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                order_number INTEGER,
                date_seen TEXT,
                title TEXT NOT NULL,
                letter_rating TEXT,
                score INTEGER,
                year_watched TEXT,
                location TEXT,
                format TEXT,
                release_year INTEGER,
                rotten_tomatoes TEXT,
                length_minutes INTEGER,
                rt_per_minute TEXT,
                genres TEXT,
                poster_url TEXT,
                rt_link TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')

        # Add missing columns if they don't exist (for existing SQLite databases)
        try:
            cursor.execute('ALTER TABLE films ADD COLUMN genres TEXT')
        except:
            pass
        try:
            cursor.execute('ALTER TABLE films ADD COLUMN poster_url TEXT')
        except:
            pass
        try:
            cursor.execute('ALTER TABLE films ADD COLUMN rt_link TEXT')
        except:
            pass

    conn.commit()
    conn.close()

def row_to_dict(row):
    """Convert database row to dictionary (works for both SQLite and PostgreSQL)"""
    if USE_POSTGRES:
        return dict(row)
    else:
        return dict(row)

@app.route('/api/films', methods=['GET'])
def get_films():
    """Get all films with optional search/filter"""
    search = request.args.get('search', '')
    location = request.args.get('location', '')
    format_type = request.args.get('format', '')
    min_score = request.args.get('min_score', '')

    conn = get_db()
    if USE_POSTGRES:
        cursor = conn.cursor(cursor_factory=RealDictCursor)
    else:
        cursor = conn.cursor()

    # Use %s for PostgreSQL, ? for SQLite
    placeholder = '%s' if USE_POSTGRES else '?'

    query = 'SELECT * FROM films WHERE 1=1'
    params = []

    if search:
        query += f' AND title LIKE {placeholder}'
        params.append(f'%{search}%')

    if location:
        query += f' AND location LIKE {placeholder}'
        params.append(f'%{location}%')

    if format_type:
        query += f' AND format LIKE {placeholder}'
        params.append(f'%{format_type}%')

    if min_score:
        query += f' AND score >= {placeholder}'
        params.append(int(min_score))

    query += ' ORDER BY order_number ASC'

    cursor.execute(query, params)
    films = [row_to_dict(row) for row in cursor.fetchall()]
    conn.close()

    return jsonify(films)

@app.route('/api/films/<int:film_id>', methods=['GET'])
def get_film(film_id):
    """Get a single film by ID"""
    conn = get_db()
    if USE_POSTGRES:
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        cursor.execute('SELECT * FROM films WHERE id = %s', (film_id,))
    else:
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM films WHERE id = ?', (film_id,))

    film = cursor.fetchone()
    conn.close()

    if film is None:
        return jsonify({'error': 'Film not found'}), 404

    return jsonify(row_to_dict(film))

def generate_rt_url(title):
    """Generate Rotten Tomatoes URL from movie title"""
    # Remove special characters and convert to lowercase
    slug = re.sub(r'[^\w\s-]', '', title.lower())
    # Replace spaces with underscores
    slug = re.sub(r'[\s]+', '_', slug)
    return f"https://www.rottentomatoes.com/m/{slug}"

@app.route('/api/films', methods=['POST'])
def add_film():
    """Add a new film with automatic metadata fetching from TMDB"""
    data = request.get_json()

    required_fields = ['title']
    if not all(field in data for field in required_fields):
        return jsonify({'error': 'Missing required fields'}), 400

    # Check for duplicates by title
    conn = get_db()
    if USE_POSTGRES:
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        cursor.execute('SELECT id, title, release_year, rt_link FROM films WHERE title = %s', (data['title'],))
    else:
        cursor = conn.cursor()
        cursor.execute('SELECT id, title, release_year, rt_link FROM films WHERE title = ?', (data['title'],))

    existing_films = cursor.fetchall()

    # If duplicates exist and user hasn't provided RT URL to distinguish, return warning
    if existing_films and not data.get('rt_link'):
        duplicate_info = []
        for film in existing_films:
            if USE_POSTGRES:
                duplicate_info.append({
                    'id': film['id'],
                    'title': film['title'],
                    'release_year': film['release_year'],
                    'rt_link': film['rt_link']
                })
            else:
                duplicate_info.append({
                    'id': film[0],
                    'title': film[1],
                    'release_year': film[2],
                    'rt_link': film[3]
                })
        conn.close()
        return jsonify({
            'duplicate': True,
            'message': 'A film with this title already exists. Please provide the Rotten Tomatoes URL to distinguish between versions.',
            'existing_films': duplicate_info
        }), 409

    conn.close()

    # Initialize variables with user-provided data
    poster_url = data.get('poster_url')
    release_year = data.get('release_year')
    length_minutes = data.get('length_minutes')
    genres = data.get('genres')
    rotten_tomatoes = data.get('rotten_tomatoes')

    # Fetch metadata from TMDB if API key is available
    if os.getenv('TMDB_API_KEY'):
        try:
            # Search for the movie
            movie_data = search_movie(data['title'], release_year)

            if movie_data:
                # Get poster if not already provided
                if not poster_url:
                    poster_url = movie_data.get('poster_url')

                # Get genres if not already provided
                if not genres:
                    genres = movie_data.get('genres')

                # Get detailed info (runtime, release year) if we have a TMDB ID
                tmdb_id = movie_data.get('tmdb_id')
                if tmdb_id:
                    details = get_movie_details(tmdb_id)
                    if details:
                        if not length_minutes:
                            length_minutes = details.get('runtime')
                        if not release_year and details.get('release_date'):
                            release_year = int(details['release_date'][:4])

                print(f"✓ Fetched metadata for '{data['title']}'")
        except Exception as e:
            print(f"Error fetching TMDB data: {e}")

    # Generate RT link if not provided
    rt_link = data.get('rt_link')
    if not rt_link:
        rt_link = generate_rt_url(data['title'])

    # Get RT percentage score (separate from link)
    rotten_tomatoes = data.get('rotten_tomatoes')

    conn = get_db()
    cursor = conn.cursor()

    if USE_POSTGRES:
        cursor.execute('''
            INSERT INTO films (order_number, date_seen, title, letter_rating, score,
                              year_watched, location, format, release_year,
                              rotten_tomatoes, length_minutes, rt_per_minute, poster_url, genres, rt_link)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            RETURNING id
        ''', (
            data.get('order_number'),
            data.get('date_seen'),
            data['title'],
            data.get('letter_rating'),
            data.get('score'),
            data.get('year_watched'),
            data.get('location'),
            data.get('format'),
            release_year,
            rotten_tomatoes,
            length_minutes,
            data.get('rt_per_minute'),
            poster_url,
            genres,
            rt_link
        ))
        film_id = cursor.fetchone()[0]
    else:
        cursor.execute('''
            INSERT INTO films (order_number, date_seen, title, letter_rating, score,
                              year_watched, location, format, release_year,
                              rotten_tomatoes, length_minutes, rt_per_minute, poster_url, genres, rt_link)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            data.get('order_number'),
            data.get('date_seen'),
            data['title'],
            data.get('letter_rating'),
            data.get('score'),
            data.get('year_watched'),
            data.get('location'),
            data.get('format'),
            release_year,
            rotten_tomatoes,
            length_minutes,
            data.get('rt_per_minute'),
            poster_url,
            genres,
            rt_link
        ))
        film_id = cursor.lastrowid

    conn.commit()
    conn.close()

    return jsonify({
        'id': film_id,
        'message': 'Film added successfully',
        'metadata_fetched': bool(poster_url or genres or length_minutes)
    }), 201

@app.route('/api/films/<int:film_id>', methods=['PUT'])
def update_film(film_id):
    """Update an existing film"""
    data = request.get_json()

    conn = get_db()
    cursor = conn.cursor()

    if USE_POSTGRES:
        cursor.execute('''
            UPDATE films
            SET order_number = %s, date_seen = %s, title = %s, letter_rating = %s,
                score = %s, year_watched = %s, location = %s, format = %s,
                release_year = %s, rotten_tomatoes = %s, length_minutes = %s, rt_per_minute = %s, rt_link = %s
            WHERE id = %s
        ''', (
            data.get('order_number'),
            data.get('date_seen'),
            data.get('title'),
            data.get('letter_rating'),
            data.get('score'),
            data.get('year_watched'),
            data.get('location'),
            data.get('format'),
            data.get('release_year'),
            data.get('rotten_tomatoes'),
            data.get('length_minutes'),
            data.get('rt_per_minute'),
            data.get('rt_link'),
            film_id
        ))
    else:
        cursor.execute('''
            UPDATE films
            SET order_number = ?, date_seen = ?, title = ?, letter_rating = ?,
                score = ?, year_watched = ?, location = ?, format = ?,
                release_year = ?, rotten_tomatoes = ?, length_minutes = ?, rt_per_minute = ?, rt_link = ?
            WHERE id = ?
        ''', (
            data.get('order_number'),
            data.get('date_seen'),
            data.get('title'),
            data.get('letter_rating'),
            data.get('score'),
            data.get('year_watched'),
            data.get('location'),
            data.get('format'),
            data.get('release_year'),
            data.get('rotten_tomatoes'),
            data.get('length_minutes'),
            data.get('rt_per_minute'),
            data.get('rt_link'),
            film_id
        ))

    conn.commit()

    if cursor.rowcount == 0:
        conn.close()
        return jsonify({'error': 'Film not found'}), 404

    conn.close()
    return jsonify({'message': 'Film updated successfully'})

@app.route('/api/films/<int:film_id>', methods=['DELETE'])
def delete_film(film_id):
    """Delete a film"""
    conn = get_db()
    cursor = conn.cursor()

    if USE_POSTGRES:
        cursor.execute('DELETE FROM films WHERE id = %s', (film_id,))
    else:
        cursor.execute('DELETE FROM films WHERE id = ?', (film_id,))

    conn.commit()

    if cursor.rowcount == 0:
        conn.close()
        return jsonify({'error': 'Film not found'}), 404

    conn.close()
    return jsonify({'message': 'Film deleted successfully'})

@app.route('/api/analytics/by-year', methods=['GET'])
def get_analytics_by_year():
    """Get analytics data grouped by year watched"""
    conn = get_db()
    if USE_POSTGRES:
        cursor = conn.cursor(cursor_factory=RealDictCursor)
    else:
        cursor = conn.cursor()

    cursor.execute('''
        SELECT year_watched, COUNT(*) as count, ROUND(AVG(score), 2) as avg_score
        FROM films
        WHERE year_watched IS NOT NULL
        AND year_watched != ''
        GROUP BY year_watched
        ORDER BY
            CASE
                WHEN year_watched = 'Pre-2006' THEN 0
                ELSE CAST(year_watched AS INTEGER)
            END
    ''')
    data = [row_to_dict(row) for row in cursor.fetchall()]
    conn.close()
    return jsonify(data)

@app.route('/api/analytics/by-film-year', methods=['GET'])
def get_analytics_by_film_year():
    """Get analytics data grouped by film release year (by decade)"""
    conn = get_db()
    if USE_POSTGRES:
        cursor = conn.cursor(cursor_factory=RealDictCursor)
    else:
        cursor = conn.cursor()

    cursor.execute('''
        SELECT
            CASE
                WHEN release_year < 1950 THEN 'Pre-1950'
                ELSE CAST((release_year / 10) * 10 AS TEXT) || 's'
            END as decade,
            COUNT(*) as count,
            ROUND(AVG(score), 2) as avg_score
        FROM films
        WHERE release_year IS NOT NULL
        GROUP BY decade
        ORDER BY
            CASE
                WHEN decade = 'Pre-1950' THEN 0
                ELSE CAST(SUBSTR(decade, 1, 4) AS INTEGER)
            END
    ''')
    data = [row_to_dict(row) for row in cursor.fetchall()]
    conn.close()
    return jsonify(data)

@app.route('/api/analytics/by-rt-score', methods=['GET'])
def get_analytics_by_rt_score():
    """Get analytics data grouped by Rotten Tomatoes score ranges"""
    conn = get_db()
    if USE_POSTGRES:
        cursor = conn.cursor(cursor_factory=RealDictCursor)
    else:
        cursor = conn.cursor()

    cursor.execute('''
        SELECT
            CASE
                WHEN CAST(REPLACE(rotten_tomatoes, '%', '') AS INTEGER) >= 90 THEN '90-100%'
                WHEN CAST(REPLACE(rotten_tomatoes, '%', '') AS INTEGER) >= 80 THEN '80-89%'
                WHEN CAST(REPLACE(rotten_tomatoes, '%', '') AS INTEGER) >= 70 THEN '70-79%'
                WHEN CAST(REPLACE(rotten_tomatoes, '%', '') AS INTEGER) >= 60 THEN '60-69%'
                WHEN CAST(REPLACE(rotten_tomatoes, '%', '') AS INTEGER) >= 50 THEN '50-59%'
                WHEN CAST(REPLACE(rotten_tomatoes, '%', '') AS INTEGER) >= 40 THEN '40-49%'
                WHEN CAST(REPLACE(rotten_tomatoes, '%', '') AS INTEGER) >= 30 THEN '30-39%'
                WHEN CAST(REPLACE(rotten_tomatoes, '%', '') AS INTEGER) >= 20 THEN '20-29%'
                WHEN CAST(REPLACE(rotten_tomatoes, '%', '') AS INTEGER) >= 10 THEN '10-19%'
                ELSE '0-9%'
            END as rt_range,
            COUNT(*) as count,
            ROUND(AVG(score), 2) as avg_score
        FROM films
        WHERE rotten_tomatoes IS NOT NULL
        AND rotten_tomatoes != ''
        GROUP BY rt_range
        ORDER BY
            CASE rt_range
                WHEN '90-100%' THEN 1
                WHEN '80-89%' THEN 2
                WHEN '70-79%' THEN 3
                WHEN '60-69%' THEN 4
                WHEN '50-59%' THEN 5
                WHEN '40-49%' THEN 6
                WHEN '30-39%' THEN 7
                WHEN '20-29%' THEN 8
                WHEN '10-19%' THEN 9
                WHEN '0-9%' THEN 10
            END
    ''')
    data = [row_to_dict(row) for row in cursor.fetchall()]
    conn.close()
    return jsonify(data)

@app.route('/api/analytics/by-genre', methods=['GET'])
def get_analytics_by_genre():
    """Get analytics data grouped by genre, sorted by count descending"""
    conn = get_db()
    if USE_POSTGRES:
        cursor = conn.cursor(cursor_factory=RealDictCursor)
    else:
        cursor = conn.cursor()

    # Get all genres (films can have multiple genres separated by comma)
    cursor.execute('''
        SELECT genres, score
        FROM films
        WHERE genres IS NOT NULL
        AND genres != ''
    ''')

    films_with_genres = cursor.fetchall()

    # Count occurrences of each genre and calculate average scores
    genre_stats = {}
    for row in films_with_genres:
        row_dict = row_to_dict(row)
        genres = row_dict['genres'].split(', ')
        score = row_dict['score']

        for genre in genres:
            genre = genre.strip()
            if genre not in genre_stats:
                genre_stats[genre] = {'count': 0, 'scores': []}
            genre_stats[genre]['count'] += 1
            if score:
                genre_stats[genre]['scores'].append(score)

    # Convert to list format and calculate averages
    data = []
    for genre, stats in genre_stats.items():
        avg_score = round(sum(stats['scores']) / len(stats['scores']), 2) if stats['scores'] else None
        data.append({
            'genre': genre,
            'count': stats['count'],
            'avg_score': avg_score
        })

    # Sort by count descending
    data.sort(key=lambda x: x['count'], reverse=True)

    conn.close()
    return jsonify(data)

@app.route('/api/admin/init-db', methods=['POST'])
def init_database():
    """Initialize database tables (admin only)"""
    try:
        init_db()
        return jsonify({
            'success': True,
            'message': 'Database initialized successfully',
            'database_type': 'PostgreSQL' if USE_POSTGRES else 'SQLite'
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/admin/import-from-json', methods=['POST'])
def import_from_json():
    """Import films from JSON file (admin only - for data migration)"""
    import json

    try:
        # Read the JSON export file
        json_file = os.path.join(os.path.dirname(__file__), 'films_export.json')
        with open(json_file, 'r', encoding='utf-8') as f:
            films = json.load(f)

        conn = get_db()
        cursor = conn.cursor()

        # Clear existing data
        if USE_POSTGRES:
            cursor.execute('DELETE FROM films')
        else:
            cursor.execute('DELETE FROM films')
        conn.commit()

        # Insert all films
        inserted = 0
        for film in films:
            if USE_POSTGRES:
                cursor.execute('''
                    INSERT INTO films (
                        order_number, date_seen, title, letter_rating, score,
                        year_watched, location, format, release_year,
                        rotten_tomatoes, length_minutes, rt_per_minute,
                        poster_url, genres, rt_link, created_at
                    )
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                ''', (
                    film.get('order_number'),
                    film.get('date_seen'),
                    film.get('title'),
                    film.get('letter_rating'),
                    film.get('score'),
                    film.get('year_watched'),
                    film.get('location'),
                    film.get('format'),
                    film.get('release_year'),
                    film.get('rotten_tomatoes'),
                    film.get('length_minutes'),
                    film.get('rt_per_minute'),
                    film.get('poster_url'),
                    film.get('genres'),
                    film.get('rt_link'),
                    film.get('created_at')
                ))
            else:
                cursor.execute('''
                    INSERT INTO films (
                        order_number, date_seen, title, letter_rating, score,
                        year_watched, location, format, release_year,
                        rotten_tomatoes, length_minutes, rt_per_minute,
                        poster_url, genres, rt_link, created_at
                    )
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    film.get('order_number'),
                    film.get('date_seen'),
                    film.get('title'),
                    film.get('letter_rating'),
                    film.get('score'),
                    film.get('year_watched'),
                    film.get('location'),
                    film.get('format'),
                    film.get('release_year'),
                    film.get('rotten_tomatoes'),
                    film.get('length_minutes'),
                    film.get('rt_per_minute'),
                    film.get('poster_url'),
                    film.get('genres'),
                    film.get('rt_link'),
                    film.get('created_at')
                ))
            inserted += 1

        conn.commit()
        conn.close()

        return jsonify({
            'success': True,
            'message': f'Successfully imported {inserted} films',
            'database_type': 'PostgreSQL' if USE_POSTGRES else 'SQLite'
        })

    except FileNotFoundError:
        return jsonify({
            'success': False,
            'error': 'films_export.json not found'
        }), 404
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

if __name__ == '__main__':
    init_db()
    port = int(os.getenv('PORT', os.getenv('FLASK_RUN_PORT', 5001)))
    app.run(debug=True, port=port)
