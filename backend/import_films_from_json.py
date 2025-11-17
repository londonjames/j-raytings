#!/usr/bin/env python3
"""
Import films from JSON file to PostgreSQL database
Usage: DATABASE_URL='postgresql://...' python3 import_films_from_json.py
"""

import json
import os
import sys
from urllib.parse import urlparse
import psycopg2
from psycopg2.extras import RealDictCursor

INPUT_FILE = 'films_export.json'

def import_films():
    """Import films from JSON to PostgreSQL"""

    # Check for DATABASE_URL
    DATABASE_URL = os.getenv('DATABASE_URL')
    if not DATABASE_URL:
        print("✗ Error: DATABASE_URL environment variable not set")
        print("Usage: DATABASE_URL='postgresql://...' python3 import_films_from_json.py")
        sys.exit(1)

    # Parse DATABASE_URL
    result = urlparse(DATABASE_URL)
    DB_CONFIG = {
        'dbname': result.path[1:],
        'user': result.username,
        'password': result.password,
        'host': result.hostname,
        'port': result.port
    }

    try:
        # Read JSON file
        with open(INPUT_FILE, 'r', encoding='utf-8') as f:
            films = json.load(f)

        print(f"✓ Loaded {len(films)} films from {INPUT_FILE}")

        # Connect to PostgreSQL
        conn = psycopg2.connect(**DB_CONFIG)
        cursor = conn.cursor()

        # Create table if it doesn't exist
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
        conn.commit()

        print("✓ Table created/verified")

        # Clear existing data (optional - remove if you want to append instead)
        cursor.execute('DELETE FROM films')
        conn.commit()
        print("✓ Cleared existing data")

        # Insert films
        inserted = 0
        for film in films:
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
            inserted += 1

        conn.commit()
        conn.close()

        print(f"✓ Successfully imported {inserted} films to PostgreSQL")

    except FileNotFoundError:
        print(f"✗ Error: {INPUT_FILE} not found")
        print("Run export_films_to_json.py first to create the export file")
        sys.exit(1)
    except Exception as e:
        print(f"✗ Error importing films: {e}")
        sys.exit(1)

if __name__ == '__main__':
    import_films()
