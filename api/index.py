from flask import Flask, request, jsonify
from flask_cors import CORS
import sqlite3
import os

try:
    from serverless_wsgi import handle_request
    SERVERLESS_WSGI_AVAILABLE = True
except ImportError:
    SERVERLESS_WSGI_AVAILABLE = False
    handle_request = None

app = Flask(__name__)
CORS(app)

# Use absolute path for database
# In Vercel, the working directory is the project root
# Don't check if file exists at import time - do it lazily when needed
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATABASE = os.path.join(BASE_DIR, 'backend', 'films.db')

def get_db():
    """Get database connection"""
    # Try multiple paths in case the database is in a different location
    db_paths = [
        DATABASE,
        os.path.join(os.path.dirname(os.path.dirname(__file__)), 'backend', 'films.db'),
        os.path.join('/var/task', 'backend', 'films.db'),  # Vercel's function directory
        'backend/films.db',  # Simple relative path
    ]
    
    db_file = None
    for path in db_paths:
        if os.path.exists(path):
            db_file = path
            break
    
    if not db_file:
        # Try to use the first path anyway - SQLite will create if needed, but we want existing
        db_file = DATABASE
        if not os.path.exists(db_file):
            raise FileNotFoundError(f"Database file not found. Tried: {db_paths}. Current working directory: {os.getcwd()}")
    
    conn = sqlite3.connect(db_file)
    conn.row_factory = sqlite3.Row
    return conn

@app.route('/api/films', methods=['GET'])
def get_films():
    """Get all films"""
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM films ORDER BY score DESC')
    films = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return jsonify(films)

@app.route('/api/films/<int:film_id>', methods=['GET'])
def get_film(film_id):
    """Get a specific film"""
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM films WHERE id = ?', (film_id,))
    film = cursor.fetchone()
    conn.close()

    if film:
        return jsonify(dict(film))
    return jsonify({'error': 'Film not found'}), 404

@app.route('/api/films', methods=['POST'])
def create_film():
    """Create a new film"""
    data = request.json
    conn = get_db()
    cursor = conn.cursor()

    cursor.execute('''
        INSERT INTO films (order_number, date_seen, title, letter_rating, score,
                          year_watched, location, format, release_year, length_minutes,
                          rotten_tomatoes, rt_per_minute, poster_url, genres)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
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
        data.get('length_minutes'),
        data.get('rotten_tomatoes'),
        data.get('rt_per_minute'),
        data.get('poster_url'),
        data.get('genres')
    ))

    conn.commit()
    film_id = cursor.lastrowid
    conn.close()

    return jsonify({'id': film_id}), 201

@app.route('/api/films/<int:film_id>', methods=['PUT'])
def update_film(film_id):
    """Update a film"""
    data = request.json
    conn = get_db()
    cursor = conn.cursor()

    cursor.execute('''
        UPDATE films
        SET order_number = ?, date_seen = ?, title = ?, letter_rating = ?,
            score = ?, year_watched = ?, location = ?, format = ?,
            release_year = ?, length_minutes = ?, rotten_tomatoes = ?,
            rt_per_minute = ?, poster_url = ?, genres = ?
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
        data.get('length_minutes'),
        data.get('rotten_tomatoes'),
        data.get('rt_per_minute'),
        data.get('poster_url'),
        data.get('genres'),
        film_id
    ))

    conn.commit()
    conn.close()

    return jsonify({'success': True})

@app.route('/api/films/<int:film_id>', methods=['DELETE'])
def delete_film(film_id):
    """Delete a film"""
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('DELETE FROM films WHERE id = ?', (film_id,))
    conn.commit()
    conn.close()

    return jsonify({'success': True})

@app.route('/api/analytics/by-year', methods=['GET'])
def analytics_by_year():
    """Get analytics by year watched"""
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('''
        SELECT
            year_watched,
            COUNT(*) as count,
            AVG(score) as avg_score
        FROM films
        WHERE year_watched IS NOT NULL AND year_watched != ''
        GROUP BY year_watched
        ORDER BY
            CASE
                WHEN year_watched = 'Pre-2006' THEN 0
                ELSE CAST(year_watched AS INTEGER)
            END
    ''')
    results = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return jsonify(results)

@app.route('/api/analytics/by-film-year', methods=['GET'])
def analytics_by_film_year():
    """Get analytics by film release decade"""
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('''
        SELECT
            CASE
                WHEN release_year < 1950 THEN 'Pre-1950'
                WHEN release_year >= 1950 AND release_year < 1960 THEN '1950s'
                WHEN release_year >= 1960 AND release_year < 1970 THEN '1960s'
                WHEN release_year >= 1970 AND release_year < 1980 THEN '1970s'
                WHEN release_year >= 1980 AND release_year < 1990 THEN '1980s'
                WHEN release_year >= 1990 AND release_year < 2000 THEN '1990s'
                WHEN release_year >= 2000 AND release_year < 2010 THEN '2000s'
                WHEN release_year >= 2010 AND release_year < 2020 THEN '2010s'
                WHEN release_year >= 2020 THEN '2020s'
            END as decade,
            COUNT(*) as count,
            AVG(score) as avg_score
        FROM films
        WHERE release_year IS NOT NULL
        GROUP BY decade
        ORDER BY
            CASE decade
                WHEN 'Pre-1950' THEN 0
                WHEN '1950s' THEN 1
                WHEN '1960s' THEN 2
                WHEN '1970s' THEN 3
                WHEN '1980s' THEN 4
                WHEN '1990s' THEN 5
                WHEN '2000s' THEN 6
                WHEN '2010s' THEN 7
                WHEN '2020s' THEN 8
            END
    ''')
    results = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return jsonify(results)

@app.route('/api/analytics/by-rt-score', methods=['GET'])
def analytics_by_rt_score():
    """Get analytics by Rotten Tomatoes score range"""
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('''
        SELECT
            CASE
                WHEN CAST(REPLACE(rotten_tomatoes, '%', '') AS INTEGER) < 60 THEN '0-59'
                WHEN CAST(REPLACE(rotten_tomatoes, '%', '') AS INTEGER) >= 60
                     AND CAST(REPLACE(rotten_tomatoes, '%', '') AS INTEGER) < 70 THEN '60-69'
                WHEN CAST(REPLACE(rotten_tomatoes, '%', '') AS INTEGER) >= 70
                     AND CAST(REPLACE(rotten_tomatoes, '%', '') AS INTEGER) < 80 THEN '70-79'
                WHEN CAST(REPLACE(rotten_tomatoes, '%', '') AS INTEGER) >= 80
                     AND CAST(REPLACE(rotten_tomatoes, '%', '') AS INTEGER) < 90 THEN '80-89'
                WHEN CAST(REPLACE(rotten_tomatoes, '%', '') AS INTEGER) >= 90 THEN '90-100'
            END as rt_range,
            COUNT(*) as count,
            AVG(score) as avg_score
        FROM films
        WHERE rotten_tomatoes IS NOT NULL AND rotten_tomatoes != ''
        GROUP BY rt_range
        ORDER BY rt_range
    ''')
    results = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return jsonify(results)

@app.route('/api/analytics/by-genre', methods=['GET'])
def analytics_by_genre():
    """Get analytics by genre"""
    conn = get_db()
    cursor = conn.cursor()

    # Get all films with genres
    cursor.execute('SELECT genres, score FROM films WHERE genres IS NOT NULL AND genres != ""')
    films = cursor.fetchall()

    # Count films and scores by genre
    genre_stats = {}
    for film in films:
        genres_list = film[0].split(', ')
        score = film[1]
        for genre in genres_list:
            genre = genre.strip()
            if genre not in genre_stats:
                genre_stats[genre] = {'count': 0, 'total_score': 0}
            genre_stats[genre]['count'] += 1
            genre_stats[genre]['total_score'] += score

    # Calculate averages
    results = []
    for genre, stats in genre_stats.items():
        results.append({
            'genre': genre,
            'count': stats['count'],
            'avg_score': stats['total_score'] / stats['count']
        })

    # Sort by count descending
    results.sort(key=lambda x: x['count'], reverse=True)

    conn.close()
    return jsonify(results)

# Vercel serverless function handler
# Vercel Python runtime passes (event, context) to the handler
def handler(event, context):
    if SERVERLESS_WSGI_AVAILABLE and handle_request:
        # serverless-wsgi handles the WSGI conversion
        return handle_request(app, event, context)
    else:
        # Fallback - should not happen in Vercel
        return {
            'statusCode': 500,
            'headers': {'Content-Type': 'application/json'},
            'body': '{"error": "serverless-wsgi not available"}'
        }
