from flask import Flask, request, jsonify
from flask_cors import CORS
import sqlite3
import os
from tmdb_service import search_movie, get_movie_details
import re
from urllib.parse import urlparse
import requests

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
                a_grade_rank INTEGER,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Add missing columns if they don't exist (for existing PostgreSQL databases)
        # Check and add date_seen if missing
        cursor.execute("""
            SELECT column_name 
            FROM information_schema.columns 
            WHERE table_name='films' AND column_name='date_seen'
        """)
        if not cursor.fetchone():
            try:
                cursor.execute('ALTER TABLE films ADD COLUMN date_seen TEXT')
                print("Added date_seen column to PostgreSQL database")
            except Exception as e:
                print(f"Error adding date_seen column: {e}")
        
        # Check and add other missing columns
        for column_name, column_type in [('genres', 'TEXT'), ('poster_url', 'TEXT'), ('rt_link', 'TEXT'), ('a_grade_rank', 'INTEGER'), ('updated_at', 'TIMESTAMP')]:
            cursor.execute("""
                SELECT column_name 
                FROM information_schema.columns 
                WHERE table_name='films' AND column_name=%s
            """, (column_name,))
            if not cursor.fetchone():
                try:
                    cursor.execute(f'ALTER TABLE films ADD COLUMN {column_name} {column_type}')
                    print(f"Added {column_name} column to PostgreSQL database")
                except Exception as e:
                    print(f"Error adding {column_name} column: {e}")
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
                a_grade_rank INTEGER,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
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

def init_books_db():
    """Initialize the books database"""
    conn = get_db()
    cursor = conn.cursor()

    if USE_POSTGRES:
        # PostgreSQL syntax
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS books (
                id SERIAL PRIMARY KEY,
                order_number INTEGER,
                date_read TEXT,
                year INTEGER,
                book_name TEXT NOT NULL,
                author TEXT,
                details_commentary TEXT,
                j_rayting TEXT,
                score INTEGER,
                type TEXT,
                pages INTEGER,
                form TEXT,
                notes_in_notion TEXT,
                cover_url TEXT,
                google_books_id TEXT,
                isbn TEXT,
                average_rating REAL,
                ratings_count INTEGER,
                published_date TEXT,
                year_written INTEGER,
                description TEXT,
                a_grade_rank INTEGER,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Add missing columns if they don't exist (for existing PostgreSQL databases)
        for column_name, column_type in [
            ('cover_url', 'TEXT'), ('google_books_id', 'TEXT'), ('isbn', 'TEXT'),
            ('average_rating', 'REAL'), ('ratings_count', 'INTEGER'),
            ('published_date', 'TEXT'), ('year_written', 'INTEGER'), ('description', 'TEXT'),
            ('notion_link', 'TEXT'), ('a_grade_rank', 'INTEGER')
        ]:
            cursor.execute("""
                SELECT column_name 
                FROM information_schema.columns 
                WHERE table_name='books' AND column_name=%s
            """, (column_name,))
            if not cursor.fetchone():
                try:
                    cursor.execute(f'ALTER TABLE books ADD COLUMN {column_name} {column_type}')
                    print(f"Added {column_name} column to PostgreSQL database")
                except Exception as e:
                    print(f"Error adding {column_name} column: {e}")
    else:
        # SQLite syntax
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS books (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                order_number INTEGER,
                date_read TEXT,
                year INTEGER,
                book_name TEXT NOT NULL,
                author TEXT,
                details_commentary TEXT,
                j_rayting TEXT,
                score INTEGER,
                type TEXT,
                pages INTEGER,
                form TEXT,
                notes_in_notion TEXT,
                cover_url TEXT,
                google_books_id TEXT,
                isbn TEXT,
                average_rating REAL,
                ratings_count INTEGER,
                published_date TEXT,
                year_written INTEGER,
                description TEXT,
                a_grade_rank INTEGER,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')

        # Add missing columns if they don't exist (for existing SQLite databases)
        for column_name, column_type in [
            ('cover_url', 'TEXT'), ('google_books_id', 'TEXT'), ('isbn', 'TEXT'),
            ('average_rating', 'REAL'), ('ratings_count', 'INTEGER'),
            ('published_date', 'TEXT'), ('description', 'TEXT'), ('year_written', 'INTEGER'),
            ('notion_link', 'TEXT'), ('a_grade_rank', 'INTEGER')
        ]:
            try:
                cursor.execute(f'ALTER TABLE books ADD COLUMN {column_name} {column_type}')
            except:
                pass

    conn.commit()
    conn.close()

def simplify_format(format_str):
    """Simplify format to standard categories"""
    if not format_str:
        return format_str

    format_lower = format_str.lower()

    # Streaming services
    streaming_services = ['hbo', 'netflix', 'amazon', 'prime', 'hulu', 'disney+',
                         'apple tv', 'peacock', 'paramount+', 'max', 'on-demand', 'ppv']
    if any(service in format_lower for service in streaming_services):
        return 'Streaming'

    # Keep these as-is
    standard_formats = ['theatre', 'dvd', 'vhs', 'blu-ray', 'plane']
    for fmt in standard_formats:
        if fmt in format_lower:
            return fmt.title()

    return format_str

def simplify_location(location_str):
    """Standardize location names and fix spelling errors"""
    if not location_str:
        return location_str

    location_lower = location_str.lower().strip()

    # Standardize common abbreviations and misspellings
    # Use exact matches only for short abbreviations
    exact_match_map = {
        'la': 'Los Angeles',
        'dc': 'Washington DC',
        'd.c.': 'Washington DC',
    }

    # Check exact match first
    if location_lower in exact_match_map:
        return exact_match_map[location_lower]

    # Substring matches for misspellings (these are safe)
    substring_map = {
        'san fran': 'San Francisco',
        'new zeal': 'New Zealand',
        'famly camp': 'Family Camp',
        # Fix Peninsula misspellings
        'peninsual': 'Peninsula',
        'peninsulat': 'Peninsula',
        'peninusula': 'Peninsula',
        'pensinsula': 'Peninsula',
    }

    # Check for substring matches
    for key, value in substring_map.items():
        if key in location_lower:
            return value

    # Title case for proper formatting (capitalize each word)
    return location_str.title()

def letter_rating_to_score(letter_rating):
    """Convert letter rating to numeric score (out of 20)"""
    if not letter_rating:
        return None
    
    rating_map = {
        'A+': 20,
        'A/A+': 19,
        'A': 18,
        'A-/A': 17,
        'A-': 16,
        'B+/A-': 15,
        'B+': 14,
        'B/B+': 13,
        'B': 12,
        'B-/B': 11,
        'B-': 10,
        'C+/B-': 9,
        'C+': 8,
        'C/C+': 7,
        'C': 6,
        'C-': 5,
        'D+': 4,
        'D': 3,
    }
    
    return rating_map.get(letter_rating.strip())

def row_to_dict(row):
    """Convert database row to dictionary (works for both SQLite and PostgreSQL)"""
    film_dict = dict(row)

    # Calculate RT/Minute if we have both RT score and length
    if film_dict.get('rotten_tomatoes') and film_dict.get('length_minutes'):
        try:
            # Extract numeric RT score (remove % if present)
            rt_score = int(film_dict['rotten_tomatoes'].replace('%', ''))
            length = int(film_dict['length_minutes'])

            if length > 0:
                rt_per_min = (rt_score / length) * 100
                # Format as whole number with percentage
                film_dict['rt_per_minute'] = f"{rt_per_min:.0f}%"
        except (ValueError, AttributeError):
            # If parsing fails, leave rt_per_minute as is
            pass

    # Simplify format
    if film_dict.get('format'):
        film_dict['format'] = simplify_format(film_dict['format'])

    # Simplify location
    if film_dict.get('location'):
        film_dict['location'] = simplify_location(film_dict['location'])

    return film_dict

def book_row_to_dict(row):
    """Convert database row to dictionary for books (works for both SQLite and PostgreSQL)"""
    book_dict = dict(row)
    return book_dict

@app.route('/api/books', methods=['GET'])
def get_books():
    """Get all books with optional search/filter"""
    search = request.args.get('search', '')
    book_type = request.args.get('type', '')
    form = request.args.get('form', '')
    author = request.args.get('author', '')
    min_score = request.args.get('min_score', '')
    rating = request.args.get('rating', '')
    year = request.args.get('year', '')

    conn = get_db()
    if USE_POSTGRES:
        cursor = conn.cursor(cursor_factory=RealDictCursor)
    else:
        cursor = conn.cursor()

    # Use %s for PostgreSQL, ? for SQLite
    placeholder = '%s' if USE_POSTGRES else '?'

    query = 'SELECT * FROM books WHERE 1=1'
    params = []

    if search:
        query += f' AND (book_name LIKE {placeholder} OR author LIKE {placeholder})'
        params.append(f'%{search}%')
        params.append(f'%{search}%')

    if book_type:
        query += f' AND type = {placeholder}'
        params.append(book_type)

    if form:
        query += f' AND form = {placeholder}'
        params.append(form)

    if author:
        query += f' AND author LIKE {placeholder}'
        params.append(f'%{author}%')

    if min_score:
        query += f' AND score >= {placeholder}'
        params.append(int(min_score))

    if rating:
        query += f' AND j_rayting = {placeholder}'
        params.append(rating)

    if year:
        query += f' AND year = {placeholder}'
        params.append(int(year))

    # Order by ID descending (newest first) so newly added books appear at top
    # Fallback to order_number if ID is not available
    query += ' ORDER BY id DESC'

    cursor.execute(query, params)
    books = [book_row_to_dict(row) for row in cursor.fetchall()]
    conn.close()

    return jsonify(books)

@app.route('/api/books/<int:book_id>', methods=['GET'])
def get_book(book_id):
    """Get a single book by ID"""
    conn = get_db()
    if USE_POSTGRES:
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        cursor.execute('SELECT * FROM books WHERE id = %s', (book_id,))
    else:
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM books WHERE id = ?', (book_id,))

    book = cursor.fetchone()
    conn.close()

    if book is None:
        return jsonify({'error': 'Book not found'}), 404

    return jsonify(book_row_to_dict(book))

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

def fetch_rt_score_from_omdb(title, year=None):
    """Fetch Rotten Tomatoes score from OMDb API"""
    # Get OMDb API key from environment or use default
    omdb_api_key = os.getenv('OMDB_API_KEY', '4e9616c3')
    omdb_base_url = 'http://www.omdbapi.com/'
    
    # Handle titles in "Last, First" format (e.g., "Fugitive, The" -> "The Fugitive")
    search_title = title
    if ',' in title:
        parts = title.split(',', 1)
        if len(parts) == 2:
            search_title = f"{parts[1].strip()} {parts[0].strip()}"
    
    params = {
        'apikey': omdb_api_key,
        't': search_title,
        'type': 'movie'
    }
    
    # Only include year if we have it
    if year:
        params['y'] = year
    
    try:
        response = requests.get(omdb_base_url, params=params, timeout=5)
        response.raise_for_status()
        data = response.json()
        
        if data.get('Response') == 'True':
            # Get Rotten Tomatoes score from Ratings array
            ratings = data.get('Ratings', [])
            for rating in ratings:
                if rating.get('Source') == 'Rotten Tomatoes':
                    rt_value = rating.get('Value', '')
                    # OMDb returns RT score as "85%" or "85"
                    if rt_value:
                        # Ensure it has % sign
                        if '%' not in rt_value:
                            rt_value = f"{rt_value}%"
                        return rt_value
        return None
    except Exception as e:
        print(f"Error fetching RT score from OMDb: {e}")
        return None

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
    metadata_fetched = False

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

                metadata_fetched = True
                print(f"✓ Fetched metadata for '{data['title']}'")
        except Exception as e:
            print(f"Error fetching TMDB data: {e}")

    # Fetch Rotten Tomatoes score from OMDb if not already provided
    if not rotten_tomatoes:
        try:
            rt_score = fetch_rt_score_from_omdb(data['title'], release_year)
            if rt_score:
                rotten_tomatoes = rt_score
                metadata_fetched = True
                print(f"✓ Fetched RT score for '{data['title']}': {rt_score}")
        except Exception as e:
            print(f"Error fetching RT score: {e}")

    # Generate RT link if not provided
    rt_link = data.get('rt_link')
    if not rt_link:
        rt_link = generate_rt_url(data['title'])

    conn = get_db()
    cursor = conn.cursor()

    if USE_POSTGRES:
        # Don't include a_grade_rank in INSERT for production (column doesn't exist yet)
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
                              rotten_tomatoes, length_minutes, rt_per_minute, poster_url, genres, rt_link, a_grade_rank)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
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
            rt_link,
            data.get('a_grade_rank')
        ))
        film_id = cursor.lastrowid

    conn.commit()
    conn.close()

    return jsonify({
        'id': film_id,
        'message': 'Film added successfully',
        'metadata_fetched': metadata_fetched
    }), 201

@app.route('/api/films/<int:film_id>', methods=['PUT'])
def update_film(film_id):
    """Update an existing film"""
    data = request.get_json()

    # Fetch RT score if not provided and film doesn't have one
    # Make this non-blocking - if it fails, just use what was provided
    rotten_tomatoes = data.get('rotten_tomatoes')
    release_year = data.get('release_year')
    title = data.get('title')
    
    # Only try to fetch RT score if it's not provided in the form data
    if (rotten_tomatoes is None or rotten_tomatoes == '') and title:
        try:
            # Check current RT score in database
            check_conn = get_db()
            try:
                if USE_POSTGRES:
                    check_cursor = check_conn.cursor(cursor_factory=RealDictCursor)
                    check_cursor.execute('SELECT rotten_tomatoes FROM films WHERE id = %s', (film_id,))
                    current_film = check_cursor.fetchone()
                    current_rt = current_film['rotten_tomatoes'] if current_film else None
                else:
                    check_cursor = check_conn.cursor()
                    check_cursor.execute('SELECT rotten_tomatoes FROM films WHERE id = ?', (film_id,))
                    current_film = check_cursor.fetchone()
                    current_rt = current_film[0] if current_film else None
                
                # Only fetch if current film also doesn't have RT score
                if not current_rt or current_rt == '':
                    try:
                        rt_score = fetch_rt_score_from_omdb(title, release_year)
                        if rt_score:
                            data['rotten_tomatoes'] = rt_score
                            rotten_tomatoes = rt_score
                            print(f"✓ Fetched RT score for '{title}': {rt_score}")
                    except Exception as e:
                        print(f"Error fetching RT score (non-blocking): {e}")
                        # Continue without RT score
                else:
                    # Keep existing RT score if not being updated
                    data['rotten_tomatoes'] = current_rt
                    rotten_tomatoes = current_rt
            finally:
                check_conn.close()
        except Exception as e:
            print(f"Error checking RT score (non-blocking): {e}")
            # Continue - use whatever was provided
    
    # Use the value from data (which may have been updated above, or use original)
    if rotten_tomatoes is None:
        rotten_tomatoes = data.get('rotten_tomatoes')

    conn = None
    try:
        conn = get_db()
        cursor = conn.cursor()

        if USE_POSTGRES:
            # Build UPDATE dynamically - only update fields that are provided
            # This avoids errors if columns don't exist
            updates = []
            values = []
            
            # All film fields that can be updated
            allowed_film_fields = [
                'order_number', 'date_seen', 'title', 'letter_rating', 'score',
                'year_watched', 'location', 'format', 'release_year', 'rotten_tomatoes',
                'length_minutes', 'rt_per_minute', 'rt_link', 'genres', 'poster_url', 'a_grade_rank'
            ]
            
            for field in allowed_film_fields:
                if field in data:
                    updates.append(f'{field} = %s')
                    # Use processed rotten_tomatoes value if available, otherwise use from data
                    if field == 'rotten_tomatoes' and rotten_tomatoes is not None:
                        values.append(rotten_tomatoes)
                    else:
                        values.append(data.get(field))
            
            if updates:
                values.append(film_id)
                # Always update updated_at timestamp
                updates.append('updated_at = CURRENT_TIMESTAMP')
                query = f'UPDATE films SET {", ".join(updates)} WHERE id = %s'
                cursor.execute(query, values)
            else:
                # No fields to update
                conn.close()
                return jsonify({'error': 'No fields to update'}), 400
        else:
            # SQLite: Build UPDATE dynamically to match PostgreSQL behavior
            updates = []
            values = []
            
            allowed_film_fields = [
                'order_number', 'date_seen', 'title', 'letter_rating', 'score',
                'year_watched', 'location', 'format', 'release_year', 'rotten_tomatoes',
                'length_minutes', 'rt_per_minute', 'rt_link', 'genres', 'poster_url', 'a_grade_rank'
            ]
            
            for field in allowed_film_fields:
                if field in data:
                    updates.append(f'{field} = ?')
                    # Use processed rotten_tomatoes value if available, otherwise use from data
                    if field == 'rotten_tomatoes' and rotten_tomatoes is not None:
                        values.append(rotten_tomatoes)
                    else:
                        values.append(data.get(field))
            
            if updates:
                values.append(film_id)
                # Always update updated_at timestamp
                updates.append('updated_at = CURRENT_TIMESTAMP')
                query = f'UPDATE films SET {", ".join(updates)} WHERE id = ?'
                cursor.execute(query, values)
            else:
                conn.close()
                return jsonify({'error': 'No fields to update'}), 400

        conn.commit()

        if cursor.rowcount == 0:
            conn.close()
            return jsonify({'error': 'Film not found'}), 404

        conn.close()
        return jsonify({'message': 'Film updated successfully'})
    except Exception as e:
        if conn:
            conn.close()
        print(f"Error updating film: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({'error': f'Error updating film: {str(e)}'}), 500

@app.route('/api/admin/films/<int:film_id>/poster', methods=['PUT'])
def update_film_poster(film_id):
    """Admin endpoint to update film poster URL"""
    data = request.get_json()
    poster_url = data.get('poster_url')
    
    if not poster_url:
        return jsonify({'error': 'poster_url is required'}), 400
    
    conn = None
    try:
        conn = get_db()
        cursor = conn.cursor()
        
        if USE_POSTGRES:
            cursor.execute('UPDATE films SET poster_url = %s, updated_at = CURRENT_TIMESTAMP WHERE id = %s', (poster_url, film_id))
        else:
            cursor.execute('UPDATE films SET poster_url = ?, updated_at = CURRENT_TIMESTAMP WHERE id = ?', (poster_url, film_id))
        
        conn.commit()
        
        if cursor.rowcount == 0:
            conn.close()
            return jsonify({'error': 'Film not found'}), 404
        
        conn.close()
        return jsonify({'message': 'Poster URL updated successfully', 'film_id': film_id})
    except Exception as e:
        if conn:
            conn.close()
        print(f"Error updating poster: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({'error': f'Error updating poster: {str(e)}'}), 500

@app.route('/api/admin/films/<int:film_id>/field', methods=['PUT'])
def update_film_field(film_id):
    """Admin endpoint to update any single field of a film"""
    data = request.get_json()
    field_name = data.get('field')
    field_value = data.get('value')
    
    if not field_name:
        return jsonify({'error': 'field name is required'}), 400
    
    # Whitelist of allowed fields to update
    allowed_fields = ['poster_url', 'title', 'letter_rating', 'score', 'release_year', 
                     'rotten_tomatoes', 'length_minutes', 'genres', 'rt_link', 
                     'date_seen', 'year_watched', 'location', 'format', 'order_number', 'a_grade_rank']
    
    if field_name not in allowed_fields:
        return jsonify({'error': f'Field "{field_name}" is not allowed. Allowed fields: {", ".join(allowed_fields)}'}), 400
    
    conn = None
    try:
        conn = get_db()
        cursor = conn.cursor()
        
        if USE_POSTGRES:
            cursor.execute(f'UPDATE films SET {field_name} = %s, updated_at = CURRENT_TIMESTAMP WHERE id = %s', (field_value, film_id))
        else:
            cursor.execute(f'UPDATE films SET {field_name} = ?, updated_at = CURRENT_TIMESTAMP WHERE id = ?', (field_value, film_id))
        
        conn.commit()
        
        if cursor.rowcount == 0:
            conn.close()
            return jsonify({'error': 'Film not found'}), 404
        
        conn.close()
        return jsonify({'message': f'{field_name} updated successfully', 'film_id': film_id, 'field': field_name, 'value': field_value})
    except Exception as e:
        if conn:
            conn.close()
        print(f"Error updating field: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({'error': f'Error updating {field_name}: {str(e)}'}), 500

@app.route('/api/admin/set-a-grade-rankings', methods=['POST'])
def set_a_grade_rankings():
    """Admin endpoint to bulk set A-grade rankings"""
    data = request.get_json()
    rankings = data.get('rankings', [])  # List of {title: str, rank: int}
    
    if not rankings:
        return jsonify({'error': 'rankings array is required'}), 400
    
    conn = None
    try:
        conn = get_db()
        cursor = conn.cursor()
        
        updated = 0
        not_found = []
        
        for item in rankings:
            title = item.get('title')
            rank = item.get('rank')
            alternatives = item.get('alternatives', [])
            
            if not title or rank is None:
                continue
            
            # Try main title first, then alternatives
            titles_to_try = [title] + alternatives
            film = None
            
            for try_title in titles_to_try:
                # Find film by title (case-insensitive)
                if USE_POSTGRES:
                    cursor.execute("""
                        SELECT id FROM films 
                        WHERE LOWER(title) = LOWER(%s) AND letter_rating = 'A'
                    """, (try_title,))
                else:
                    cursor.execute("""
                        SELECT id FROM films 
                        WHERE LOWER(title) = LOWER(?) AND letter_rating = 'A'
                    """, (try_title,))
                
                film = cursor.fetchone()
                if film:
                    break  # Found it, stop trying alternatives
            
            if film:
                film_id = film[0] if USE_POSTGRES else film[0]
                
                # Check if a_grade_rank column exists
                if USE_POSTGRES:
                    cursor.execute("""
                        SELECT column_name 
                        FROM information_schema.columns 
                        WHERE table_name='films' AND column_name='a_grade_rank'
                    """)
                    if not cursor.fetchone():
                        conn.close()
                        return jsonify({'error': 'a_grade_rank column does not exist'}), 500
                
                # Update the ranking
                if USE_POSTGRES:
                    cursor.execute('UPDATE films SET a_grade_rank = %s, updated_at = CURRENT_TIMESTAMP WHERE id = %s', (rank, film_id))
                else:
                    cursor.execute('UPDATE films SET a_grade_rank = ?, updated_at = CURRENT_TIMESTAMP WHERE id = ?', (rank, film_id))
                
                updated += 1
            else:
                not_found.append(title)
        
        conn.commit()
        conn.close()
        
        return jsonify({
            'message': f'Successfully updated {updated} rankings',
            'updated': updated,
            'not_found': not_found
        })
    except Exception as e:
        if conn:
            conn.close()
        print(f"Error setting A-grade rankings: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({'error': f'Error setting rankings: {str(e)}'}), 500

@app.route('/api/admin/set-a-grade-book-rankings', methods=['POST'])
def set_a_grade_book_rankings():
    """Admin endpoint to bulk set A-grade book rankings"""
    data = request.get_json()
    rankings = data.get('rankings', [])  # List of {book_name: str, rank: int}
    
    if not rankings:
        return jsonify({'error': 'rankings array is required'}), 400
    
    conn = None
    try:
        conn = get_db()
        cursor = conn.cursor()
        
        updated = 0
        not_found = []
        
        for item in rankings:
            book_name = item.get('book_name')
            rank = item.get('rank')
            alternatives = item.get('alternatives', [])
            
            if not book_name or rank is None:
                continue
            
            # Try main book name first, then alternatives
            names_to_try = [book_name] + alternatives
            book = None
            
            for try_name in names_to_try:
                # Find book by name (case-insensitive) - check for A+ or A/A+ or A ratings
                if USE_POSTGRES:
                    cursor.execute("""
                        SELECT id FROM books 
                        WHERE LOWER(book_name) = LOWER(%s) AND j_rayting IN ('A+', 'A/A+', 'A')
                    """, (try_name,))
                else:
                    cursor.execute("""
                        SELECT id FROM books 
                        WHERE LOWER(book_name) = LOWER(?) AND j_rayting IN ('A+', 'A/A+', 'A')
                    """, (try_name,))
                
                book = cursor.fetchone()
                if book:
                    break  # Found it, stop trying alternatives
            
            if book:
                book_id = book[0] if USE_POSTGRES else book[0]
                
                # Check if a_grade_rank column exists
                if USE_POSTGRES:
                    cursor.execute("""
                        SELECT column_name 
                        FROM information_schema.columns 
                        WHERE table_name='books' AND column_name='a_grade_rank'
                    """)
                    if not cursor.fetchone():
                        conn.close()
                        return jsonify({'error': 'a_grade_rank column does not exist'}), 500
                
                # Update the ranking
                if USE_POSTGRES:
                    cursor.execute('UPDATE books SET a_grade_rank = %s, updated_at = CURRENT_TIMESTAMP WHERE id = %s', (rank, book_id))
                else:
                    cursor.execute('UPDATE books SET a_grade_rank = ?, updated_at = CURRENT_TIMESTAMP WHERE id = ?', (rank, book_id))
                
                updated += 1
            else:
                not_found.append(book_name)
        
        conn.commit()
        conn.close()
        
        return jsonify({
            'message': f'Successfully updated {updated} rankings',
            'updated': updated,
            'not_found': not_found
        })
    except Exception as e:
        if conn:
            conn.close()
        print(f"Error setting A-grade book rankings: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({'error': f'Error setting rankings: {str(e)}'}), 500

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

@app.route('/api/books', methods=['POST'])
def add_book():
    """Add a new book with automatic metadata fetching from Google Books"""
    from google_books_service import search_book
    
    data = request.get_json()

    required_fields = ['book_name']
    if not all(field in data for field in required_fields):
        return jsonify({'error': 'Missing required fields'}), 400

    # Check for duplicates by book name and author
    conn = get_db()
    if USE_POSTGRES:
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        cursor.execute('SELECT id, book_name, author FROM books WHERE book_name = %s AND author = %s', 
                      (data['book_name'], data.get('author', '')))
    else:
        cursor = conn.cursor()
        cursor.execute('SELECT id, book_name, author FROM books WHERE book_name = ? AND author = ?', 
                      (data['book_name'], data.get('author', '')))

    existing_books = cursor.fetchall()

    if existing_books:
        duplicate_info = []
        for book in existing_books:
            if USE_POSTGRES:
                duplicate_info.append({
                    'id': book['id'],
                    'book_name': book['book_name'],
                    'author': book['author']
                })
            else:
                duplicate_info.append({
                    'id': book[0],
                    'book_name': book[1],
                    'author': book[2]
                })
        conn.close()
        return jsonify({
            'duplicate': True,
            'message': 'A book with this name and author already exists.',
            'existing_books': duplicate_info
        }), 409

    conn.close()

    # Initialize variables with user-provided data
    cover_url = data.get('cover_url')
    google_books_id = data.get('google_books_id')
    isbn = data.get('isbn')
    average_rating = data.get('average_rating')
    ratings_count = data.get('ratings_count')
    published_date = data.get('published_date')
    description = data.get('description')
    pages = data.get('pages')
    metadata_fetched = False

    # Fetch metadata from Google Books API if available
    if os.getenv('GOOGLE_BOOKS_API_KEY') or True:  # API works without key
        try:
            # Search for the book
            book_data = search_book(data['book_name'], data.get('author'), data.get('isbn'))

            if book_data:
                # Get cover if not already provided
                if not cover_url:
                    cover_url = book_data.get('cover_url')

                # Get other metadata if not already provided
                if not google_books_id:
                    google_books_id = book_data.get('google_books_id')
                if not isbn:
                    isbn = book_data.get('isbn')
                if average_rating is None:
                    average_rating = book_data.get('average_rating')
                if ratings_count is None:
                    ratings_count = book_data.get('ratings_count')
                if not published_date:
                    published_date = book_data.get('published_date')
                # Extract year_written from published_date if not already set
                if not data.get('year_written') and published_date:
                    year_match = None
                    if isinstance(published_date, str):
                        year_match = published_date[:4] if len(published_date) >= 4 else None
                    elif isinstance(published_date, int):
                        year_match = str(published_date) if 0 < published_date < 3000 else None
                    if year_match and year_match.isdigit():
                        data['year_written'] = int(year_match)
                if not description:
                    description = book_data.get('description')
                # Get page count if not already provided
                if not pages and book_data.get('page_count'):
                    pages = book_data.get('page_count')

                metadata_fetched = True
                print(f"✓ Fetched metadata for '{data['book_name']}'")
                if cover_url:
                    print(f"  Cover URL: {cover_url}")
                else:
                    print(f"  ⚠️  No cover URL found for '{data['book_name']}'")
        except Exception as e:
            print(f"Error fetching Google Books data for '{data.get('book_name', 'unknown')}': {e}")
            import traceback
            traceback.print_exc()

    # Extract year from date_read if year is not provided
    year = data.get('year')
    if not year and data.get('date_read'):
        date_read = data.get('date_read')
        if isinstance(date_read, str):
            # Handle YYYY-MM-DD format (from date input) - check if first part is 4 digits
            if '-' in date_read:
                parts = date_read.split('-')
                if len(parts) >= 1:
                    try:
                        first_part = parts[0]
                        # If first part is 4 digits, it's YYYY-MM-DD format
                        if len(first_part) == 4 and first_part.isdigit():
                            year = int(first_part)
                        # Otherwise, check if it's Month-YY format (e.g., "November-22")
                        elif len(parts) == 2:
                            year_part = parts[1]
                            # Convert 2-digit year to 4-digit
                            year_int = int(year_part)
                            year = 2000 + year_int if year_int < 50 else 1900 + year_int
                    except (ValueError, IndexError):
                        pass
            # Handle MM/DD/YYYY format
            elif '/' in date_read:
                try:
                    parts = date_read.split('/')
                    if len(parts) == 3:
                        year = int(parts[2])
                except (ValueError, IndexError):
                    pass

    # Get max order_number to set new book's order
    conn = get_db()
    cursor = conn.cursor()
    if USE_POSTGRES:
        cursor.execute('SELECT COALESCE(MAX(order_number), 0) FROM books')
    else:
        cursor.execute('SELECT COALESCE(MAX(order_number), 0) FROM books')
    result = cursor.fetchone()
    max_order = result[0] if result else 0
    new_order = max_order + 1

    # Insert new book
    if USE_POSTGRES:
        # Extract year_written from published_date if not provided
        year_written = data.get('year_written')
        if not year_written and published_date:
            if isinstance(published_date, str):
                year_match = published_date[:4] if len(published_date) >= 4 else None
                if year_match and year_match.isdigit():
                    year_written = int(year_match)
            elif isinstance(published_date, int):
                if 0 < published_date < 3000:
                    year_written = published_date
        
        cursor.execute('''
            INSERT INTO books (
                order_number, date_read, year, book_name, author,
                details_commentary, j_rayting, score, type, pages,
                form, notes_in_notion, notion_link, cover_url, google_books_id,
                isbn, average_rating, ratings_count, published_date, year_written, description
            )
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            RETURNING id
        ''', (
            data.get('order_number', new_order),
            data.get('date_read'),
            year or data.get('year'),  # Use extracted year if available, otherwise user-provided
            data['book_name'],
            data.get('author'),
            data.get('details_commentary'),
            data.get('j_rayting'),
            data.get('score') or letter_rating_to_score(data.get('j_rayting')),
            data.get('type'),
            pages or data.get('pages'),  # Use fetched pages if available, otherwise user-provided
            data.get('form'),
            data.get('notes_in_notion'),
            data.get('notion_link'),
            cover_url,
            google_books_id,
            isbn,
            average_rating,
            ratings_count,
            published_date,
            year_written,
            description
        ))
        book_id = cursor.fetchone()[0]
    else:
        # Extract year_written from published_date if not provided
        year_written = data.get('year_written')
        if not year_written and published_date:
            if isinstance(published_date, str):
                year_match = published_date[:4] if len(published_date) >= 4 else None
                if year_match and year_match.isdigit():
                    year_written = int(year_match)
            elif isinstance(published_date, int):
                if 0 < published_date < 3000:
                    year_written = published_date
        
        cursor.execute('''
            INSERT INTO books (
                order_number, date_read, year, book_name, author,
                details_commentary, j_rayting, score, type, pages,
                form, notes_in_notion, notion_link, cover_url, google_books_id,
                isbn, average_rating, ratings_count, published_date, year_written, description
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            data.get('order_number', new_order),
            data.get('date_read'),
            year or data.get('year'),  # Use extracted year if available, otherwise user-provided
            data['book_name'],
            data.get('author'),
            data.get('details_commentary'),
            data.get('j_rayting'),
            data.get('score') or letter_rating_to_score(data.get('j_rayting')),
            data.get('type'),
            pages or data.get('pages'),  # Use fetched pages if available, otherwise user-provided
            data.get('form'),
            data.get('notes_in_notion'),
            data.get('notion_link'),
            cover_url,
            google_books_id,
            isbn,
            average_rating,
            ratings_count,
            published_date,
            year_written,
            description
        ))
        book_id = cursor.lastrowid

    conn.commit()
    conn.close()

    return jsonify({
        'message': 'Book added successfully',
        'book_id': book_id,
        'metadata_fetched': metadata_fetched
    }), 201

@app.route('/api/books/<int:book_id>', methods=['PUT'])
def update_book(book_id):
    """Update an existing book"""
    data = request.get_json()

    conn = get_db()
    cursor = conn.cursor()

    # Build update query dynamically based on provided fields
    updates = []
    params = []

    allowed_fields = [
        'order_number', 'date_read', 'year', 'book_name', 'author',
        'details_commentary', 'j_rayting', 'score', 'type', 'pages',
        'form', 'notes_in_notion', 'notion_link', 'cover_url', 'google_books_id',
        'isbn', 'average_rating', 'ratings_count', 'published_date', 'year_written', 'description'
    ]

    placeholder = '%s' if USE_POSTGRES else '?'
    
    # Track if j_rayting is being updated and if score is provided
    j_rayting_updated = False
    score_provided = 'score' in data
    
    for field in allowed_fields:
        if field in data:
            updates.append(f'{field} = {placeholder}')
            if field == 'j_rayting':
                j_rayting_updated = True
            params.append(data[field])
    
    # If j_rayting was updated but score wasn't provided, auto-calculate score
    if j_rayting_updated and not score_provided:
        j_rayting_value = data.get('j_rayting')
        calculated_score = letter_rating_to_score(j_rayting_value)
        if calculated_score is not None:
            updates.append(f'score = {placeholder}')
            params.append(calculated_score)

    if not updates:
        conn.close()
        return jsonify({'error': 'No valid fields to update'}), 400

    params.append(book_id)
    
    # Always update updated_at timestamp
    updates.append('updated_at = CURRENT_TIMESTAMP')

    if USE_POSTGRES:
        query = f'UPDATE books SET {", ".join(updates)} WHERE id = %s'
    else:
        query = f'UPDATE books SET {", ".join(updates)} WHERE id = ?'

    cursor.execute(query, params)
    conn.commit()

    if cursor.rowcount == 0:
        conn.close()
        return jsonify({'error': 'Book not found'}), 404

    conn.close()
    return jsonify({'message': 'Book updated successfully'})

@app.route('/api/books/<int:book_id>', methods=['DELETE'])
def delete_book(book_id):
    """Delete a book"""
    conn = get_db()
    cursor = conn.cursor()

    if USE_POSTGRES:
        cursor.execute('DELETE FROM books WHERE id = %s', (book_id,))
    else:
        cursor.execute('DELETE FROM books WHERE id = ?', (book_id,))

    conn.commit()

    if cursor.rowcount == 0:
        conn.close()
        return jsonify({'error': 'Book not found'}), 404

    conn.close()
    return jsonify({'message': 'Book deleted successfully'})

@app.route('/api/admin/books/<int:book_id>/cover', methods=['PUT'])
def update_book_cover(book_id):
    """Admin endpoint to update book cover URL"""
    from google_books_service import search_book, get_book_details
    
    data = request.get_json()
    cover_url = data.get('cover_url')
    book_name = data.get('book_name')
    author = data.get('author')
    
    conn = None
    try:
        conn = get_db()
        cursor = conn.cursor()
        
        # If cover_url not provided, try to fetch from Google Books
        if not cover_url and (book_name or author):
            book_data = search_book(book_name or '', author)
            if book_data and book_data.get('cover_url'):
                cover_url = book_data['cover_url']
        
        if not cover_url:
            return jsonify({'error': 'cover_url is required or book_name/author needed to fetch'}), 400
        
        if USE_POSTGRES:
            cursor.execute('UPDATE books SET cover_url = %s, updated_at = CURRENT_TIMESTAMP WHERE id = %s', (cover_url, book_id))
        else:
            cursor.execute('UPDATE books SET cover_url = ?, updated_at = CURRENT_TIMESTAMP WHERE id = ?', (cover_url, book_id))
        
        conn.commit()
        conn.close()
        return jsonify({'message': 'Cover updated successfully', 'cover_url': cover_url})
    except Exception as e:
        if conn:
            conn.close()
        print(f"Error updating cover: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({'error': f'Error updating cover: {str(e)}'}), 500

@app.route('/api/books/cover-proxy', methods=['GET'])
def proxy_book_cover():
    """Proxy endpoint to serve book cover images and avoid CORS issues"""
    cover_url = request.args.get('url')
    book_id = request.args.get('book_id')  # Optional: Google Books ID
    
    if not cover_url and not book_id:
        return jsonify({'error': 'url or book_id parameter is required'}), 400
    
    # If we have a book_id, try to construct a working thumbnail URL
    if book_id:
        # Try the standard Google Books thumbnail URL format
        thumbnail_urls = [
            f"https://books.google.com/books/publisher/content/images/frontcover/{book_id}?fife=w480-h690",
            f"https://books.google.com/books/content?id={book_id}&printsec=frontcover&img=1&zoom=1",
            f"http://books.google.com/books/content?id={book_id}&printsec=frontcover&img=1&zoom=1"
        ]
    else:
        thumbnail_urls = [cover_url]
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
        'Referer': 'https://books.google.com/'
    }
    
    # Try each URL until one works
    for url in thumbnail_urls:
        try:
            response = requests.get(url, timeout=10, stream=True, headers=headers, allow_redirects=True)
            response.raise_for_status()
            
            # Check if it's actually an image
            content_type = response.headers.get('Content-Type', '')
            if 'image' not in content_type:
                # Check first few bytes to see if it's an image
                content_preview = response.content[:10]
                if not (content_preview.startswith(b'\xff\xd8') or content_preview.startswith(b'\x89PNG')):
                    continue  # Try next URL
            
            # Return the image with appropriate headers
            from flask import Response
            return Response(
                response.content,
                mimetype=content_type or 'image/jpeg',
                headers={
                    'Access-Control-Allow-Origin': '*',
                    'Cache-Control': 'no-cache, no-store, must-revalidate'  # Don't cache to allow updates
                }
            )
        except requests.exceptions.RequestException:
            continue  # Try next URL
    
    # If all URLs failed, return error
    return jsonify({'error': 'Failed to fetch cover image from all attempted URLs'}), 500

@app.route('/api/admin/books/<int:book_id>/field', methods=['PUT'])
def update_book_field(book_id):
    """Admin endpoint to update a specific book field"""
    data = request.get_json()
    field_name = data.get('field')
    field_value = data.get('value')
    
    if not field_name:
        return jsonify({'error': 'field is required'}), 400
    
    # Validate field name
    allowed_fields = [
        'order_number', 'date_read', 'year', 'book_name', 'author',
        'details_commentary', 'j_rayting', 'score', 'type', 'pages',
        'form', 'notes_in_notion', 'notion_link', 'cover_url', 'google_books_id',
        'isbn', 'average_rating', 'ratings_count', 'published_date', 'year_written', 'description', 'a_grade_rank'
    ]
    
    if field_name not in allowed_fields:
        return jsonify({'error': f'Field {field_name} is not allowed'}), 400
    
    conn = None
    try:
        conn = get_db()
        cursor = conn.cursor()
        
        placeholder = '%s' if USE_POSTGRES else '?'
        
        if USE_POSTGRES:
            cursor.execute(f'UPDATE books SET {field_name} = %s, updated_at = CURRENT_TIMESTAMP WHERE id = %s', (field_value, book_id))
        else:
            cursor.execute(f'UPDATE books SET {field_name} = ?, updated_at = CURRENT_TIMESTAMP WHERE id = ?', (field_value, book_id))
        
        conn.commit()
        conn.close()
        return jsonify({'message': f'{field_name} updated successfully', 'book_id': book_id, 'field': field_name, 'value': field_value})
    except Exception as e:
        if conn:
            conn.close()
        print(f"Error updating field: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({'error': f'Error updating {field_name}: {str(e)}'}), 500

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

@app.route('/api/analytics/books/by-year', methods=['GET'])
def get_books_analytics_by_year():
    """Get books analytics data grouped by year read"""
    conn = get_db()
    if USE_POSTGRES:
        cursor = conn.cursor(cursor_factory=RealDictCursor)
    else:
        cursor = conn.cursor()

    cursor.execute('''
        SELECT year, COUNT(*) as count, ROUND(AVG(score), 2) as avg_score
        FROM books
        WHERE year IS NOT NULL
        GROUP BY year
        ORDER BY year DESC
    ''')
    data = [book_row_to_dict(row) for row in cursor.fetchall()]
    conn.close()
    return jsonify(data)

@app.route('/api/analytics/books/by-type', methods=['GET'])
def get_books_analytics_by_type():
    """Get books analytics data grouped by type"""
    conn = get_db()
    if USE_POSTGRES:
        cursor = conn.cursor(cursor_factory=RealDictCursor)
    else:
        cursor = conn.cursor()

    cursor.execute('''
        SELECT type, COUNT(*) as count, ROUND(AVG(score), 2) as avg_score
        FROM books
        WHERE type IS NOT NULL AND type != ''
        GROUP BY type
        ORDER BY count DESC
    ''')
    data = [book_row_to_dict(row) for row in cursor.fetchall()]
    conn.close()
    return jsonify(data)

@app.route('/api/analytics/books/by-form', methods=['GET'])
def get_books_analytics_by_form():
    """Get books analytics data grouped by form (Kindle vs Book)"""
    conn = get_db()
    if USE_POSTGRES:
        cursor = conn.cursor(cursor_factory=RealDictCursor)
    else:
        cursor = conn.cursor()

    cursor.execute('''
        SELECT form, COUNT(*) as count, ROUND(AVG(score), 2) as avg_score
        FROM books
        WHERE form IS NOT NULL AND form != ''
        GROUP BY form
        ORDER BY count DESC
    ''')
    data = [book_row_to_dict(row) for row in cursor.fetchall()]
    conn.close()
    return jsonify(data)

@app.route('/api/analytics/books/by-author', methods=['GET'])
def get_books_analytics_by_author():
    """Get books analytics data grouped by author (top authors)"""
    conn = get_db()
    if USE_POSTGRES:
        cursor = conn.cursor(cursor_factory=RealDictCursor)
    else:
        cursor = conn.cursor()

    cursor.execute('''
        SELECT author, COUNT(*) as count, ROUND(AVG(score), 2) as avg_score
        FROM books
        WHERE author IS NOT NULL AND author != ''
        GROUP BY author
        ORDER BY count DESC
        LIMIT 20
    ''')
    data = [book_row_to_dict(row) for row in cursor.fetchall()]
    conn.close()
    return jsonify(data)

@app.route('/api/analytics/books/summary', methods=['GET'])
def get_books_summary():
    """Get overall books summary statistics"""
    conn = get_db()
    if USE_POSTGRES:
        cursor = conn.cursor(cursor_factory=RealDictCursor)
    else:
        cursor = conn.cursor()

    cursor.execute('''
        SELECT 
            COUNT(*) as total_books,
            ROUND(AVG(score), 2) as avg_score,
            SUM(pages) as total_pages,
            ROUND(AVG(pages), 2) as avg_pages,
            ROUND(AVG(average_rating), 2) as avg_goodreads_rating
        FROM books
        WHERE pages IS NOT NULL
    ''')
    
    result = cursor.fetchone()
    if USE_POSTGRES:
        summary = dict(result)
    else:
        summary = {
            'total_books': result[0],
            'avg_score': result[1],
            'total_pages': result[2],
            'avg_pages': result[3],
            'avg_goodreads_rating': result[4]
        }
    
    conn.close()
    return jsonify(summary)

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

# Initialize database on app startup (runs every time app starts)
# Wrap in try-except to prevent deployment failures if DB isn't ready yet
try:
    init_db()
    init_books_db()
except Exception as e:
    print(f"Warning: Database initialization had an issue (this is OK if DB isn't ready yet): {e}")

if __name__ == '__main__':
    port = int(os.getenv('PORT', os.getenv('FLASK_RUN_PORT', 5001)))
    app.run(debug=True, port=port)
