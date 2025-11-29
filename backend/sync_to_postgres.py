#!/usr/bin/env python3
"""
Sync SQLite database to PostgreSQL production database
This will MERGE data - preserving films added in production while updating/inserting from SQLite
PRODUCTION IS THE SOURCE OF TRUTH - films added in production will be preserved
"""
import sqlite3
import psycopg2
from urllib.parse import urlparse
import os

# PostgreSQL connection string
DATABASE_URL = "postgresql://postgres:rcvXfFuoGQZokshoQKRJvMcZGvvweTHI@gondola.proxy.rlwy.net:57791/railway"

def main():
    print("=" * 80)
    print("SYNCING SQLITE TO POSTGRESQL")
    print("=" * 80)
    print()

    # Connect to SQLite
    print("📂 Connecting to local SQLite database...")
    sqlite_conn = sqlite3.connect('films.db')
    sqlite_conn.row_factory = sqlite3.Row
    sqlite_cursor = sqlite_conn.cursor()

    # Get count from SQLite
    sqlite_cursor.execute("SELECT COUNT(*) FROM films")
    sqlite_count = sqlite_cursor.fetchone()[0]
    print(f"✓ SQLite database has {sqlite_count} films")
    print()

    # Parse PostgreSQL URL
    result = urlparse(DATABASE_URL)

    # Connect to PostgreSQL
    print("🐘 Connecting to PostgreSQL production database...")
    pg_conn = psycopg2.connect(
        database=result.path[1:],
        user=result.username,
        password=result.password,
        host=result.hostname,
        port=result.port
    )
    pg_cursor = pg_conn.cursor()

    # Get count from PostgreSQL before
    pg_cursor.execute("SELECT COUNT(*) FROM films")
    pg_count_before = pg_cursor.fetchone()[0]
    print(f"✓ PostgreSQL currently has {pg_count_before} films")
    print()

    # Get all films from SQLite
    print("📦 Reading all films from SQLite...")
    sqlite_cursor.execute("SELECT * FROM films ORDER BY id")
    sqlite_films = sqlite_cursor.fetchall()
    print(f"✓ Retrieved {len(sqlite_films)} films from SQLite")
    print()

    # Helper function to safely get values from Row object
    def get_value(film, key, default=None):
        try:
            return film[key]
        except (KeyError, IndexError):
            return default

    # Update or insert films from SQLite
    print("⬆️  Syncing films from SQLite to PostgreSQL...")
    updated = 0
    inserted = 0
    preserved = 0

    for film in sqlite_films:
        film_id = get_value(film, 'id')
        
        # Check if film exists in PostgreSQL
        pg_cursor.execute("SELECT id FROM films WHERE id = %s", (film_id,))
        exists = pg_cursor.fetchone()
        
        # Handle optional fields safely
        location = get_value(film, 'location')
        format_val = get_value(film, 'format')
        
        if exists:
            # Update existing film
            pg_cursor.execute("""
                UPDATE films SET
                    title = %s, release_year = %s, score = %s, letter_rating = %s, year_watched = %s,
                    rotten_tomatoes = %s, length_minutes = %s, rt_per_minute = %s, poster_url = %s,
                    genres = %s, rt_link = %s, location = %s, format = %s
                WHERE id = %s
            """, (
                get_value(film, 'title'),
                get_value(film, 'release_year'),
                get_value(film, 'score'),
                get_value(film, 'letter_rating'),
                get_value(film, 'year_watched'),
                get_value(film, 'rotten_tomatoes'),
                get_value(film, 'length_minutes'),
                get_value(film, 'rt_per_minute'),
                get_value(film, 'poster_url'),
                get_value(film, 'genres'),
                get_value(film, 'rt_link'),
                location,
                format_val,
                film_id
            ))
            updated += 1
        else:
            # Insert new film
            pg_cursor.execute("""
                INSERT INTO films (
                    id, title, release_year, score, letter_rating, year_watched,
                    rotten_tomatoes, length_minutes, rt_per_minute, poster_url,
                    genres, rt_link, location, format
                ) VALUES (
                    %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s
                )
            """, (
                film_id,
                get_value(film, 'title'),
                get_value(film, 'release_year'),
                get_value(film, 'score'),
                get_value(film, 'letter_rating'),
                get_value(film, 'year_watched'),
                get_value(film, 'rotten_tomatoes'),
                get_value(film, 'length_minutes'),
                get_value(film, 'rt_per_minute'),
                get_value(film, 'poster_url'),
                get_value(film, 'genres'),
                get_value(film, 'rt_link'),
                location,
                format_val
            ))
            inserted += 1

        if (updated + inserted) % 100 == 0:
            print(f"  Processed {updated + inserted}/{len(sqlite_films)} films...")

    pg_conn.commit()
    
    # Count films that exist in PostgreSQL but not SQLite (preserved production entries)
    pg_cursor.execute("SELECT id FROM films")
    pg_all_ids = {row[0] for row in pg_cursor.fetchall()}
    sqlite_all_ids = {get_value(film, 'id') for film in sqlite_films}
    preserved_ids = pg_all_ids - sqlite_all_ids
    preserved = len(preserved_ids)
    
    print(f"✓ Updated {updated} existing films")
    print(f"✓ Inserted {inserted} new films from SQLite")
    print(f"✓ Preserved {preserved} films that exist only in PostgreSQL (added in production)")
    print()

    # Reset sequence
    print("🔧 Resetting ID sequence...")
    pg_cursor.execute("SELECT MAX(id) FROM films")
    max_id = pg_cursor.fetchone()[0]
    if max_id:
        pg_cursor.execute(f"SELECT setval('films_id_seq', {max_id})")
        pg_conn.commit()
        print(f"✓ Sequence reset to {max_id}")
    print()

    # Verify
    pg_cursor.execute("SELECT COUNT(*) FROM films")
    pg_count_after = pg_cursor.fetchone()[0]

    print("=" * 80)
    print("SYNC COMPLETE!")
    print("=" * 80)
    print(f"SQLite:     {sqlite_count} films")
    print(f"PostgreSQL: {pg_count_after} films")
    print(f"Updated:    {updated} films")
    print(f"Inserted:   {inserted} films from SQLite")
    print(f"Preserved:  {preserved} films from production (not in SQLite)")
    print()

    # Show RT score stats
    pg_cursor.execute("SELECT COUNT(*) FROM films WHERE rotten_tomatoes IS NOT NULL AND rotten_tomatoes != ''")
    with_rt = pg_cursor.fetchone()[0]
    pg_cursor.execute("SELECT COUNT(*) FROM films WHERE rotten_tomatoes = 'no RT score'")
    no_rt = pg_cursor.fetchone()[0]
    has_score = with_rt - no_rt

    print(f"RT Scores:  {has_score} films ({100*has_score/pg_count_after:.1f}%)")
    print(f"No RT:      {no_rt} films marked 'no RT score'")
    print("=" * 80)

    # Close connections
    sqlite_conn.close()
    pg_conn.close()

if __name__ == '__main__':
    main()
