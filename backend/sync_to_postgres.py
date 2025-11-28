#!/usr/bin/env python3
"""
Sync SQLite database to PostgreSQL production database
This will replace all data in PostgreSQL with the updated SQLite data
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

    # Clear PostgreSQL table
    print("🗑️  Clearing PostgreSQL films table...")
    pg_cursor.execute("DELETE FROM films")
    pg_conn.commit()
    print("✓ Cleared all existing data")
    print()

    # Get all films from SQLite
    print("📦 Reading all films from SQLite...")
    sqlite_cursor.execute("SELECT * FROM films ORDER BY id")
    films = sqlite_cursor.fetchall()
    print(f"✓ Retrieved {len(films)} films")
    print()

    # Insert into PostgreSQL
    print("⬆️  Uploading films to PostgreSQL...")
    inserted = 0

    for film in films:
        # Handle optional fields safely
        try:
            location = film['location']
        except (KeyError, IndexError):
            location = None

        try:
            format_val = film['format']
        except (KeyError, IndexError):
            format_val = None

        pg_cursor.execute("""
            INSERT INTO films (
                id, title, release_year, score, letter_rating, year_watched,
                rotten_tomatoes, length_minutes, rt_per_minute, poster_url,
                genres, rt_link, location, format
            ) VALUES (
                %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s
            )
        """, (
            film['id'],
            film['title'],
            film['release_year'],
            film['score'],
            film['letter_rating'],
            film['year_watched'],
            film['rotten_tomatoes'],
            film['length_minutes'],
            film['rt_per_minute'],
            film['poster_url'],
            film['genres'],
            film['rt_link'],
            location,
            format_val
        ))
        inserted += 1

        if inserted % 100 == 0:
            print(f"  Uploaded {inserted}/{len(films)} films...")

    pg_conn.commit()
    print(f"✓ Successfully uploaded {inserted} films")
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
    print(f"Difference: {pg_count_before - pg_count_after} films removed")
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
