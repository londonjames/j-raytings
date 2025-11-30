#!/usr/bin/env python3
"""
Sync PostgreSQL production database to SQLite local database
This will REPLACE local data with production data to ensure local matches production
PRODUCTION IS THE SOURCE OF TRUTH - all production data will be synced to local
"""
import sqlite3
import psycopg2
from urllib.parse import urlparse
import os

# PostgreSQL connection string
DATABASE_URL = "postgresql://postgres:rcvXfFuoGQZokshoQKRJvMcZGvvweTHI@gondola.proxy.rlwy.net:57791/railway"

def main():
    print("=" * 80)
    print("SYNCING POSTGRESQL TO SQLITE (FILMS)")
    print("=" * 80)
    print()
    print("⚠️  WARNING: This will REPLACE all local film data with production data!")
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

    # Get count from PostgreSQL
    pg_cursor.execute("SELECT COUNT(*) FROM films")
    pg_count = pg_cursor.fetchone()[0]
    print(f"✓ PostgreSQL database has {pg_count} films")
    print()

    # Connect to SQLite
    print("📂 Connecting to local SQLite database...")
    sqlite_conn = sqlite3.connect('films.db')
    sqlite_cursor = sqlite_conn.cursor()

    # Get count from SQLite before
    sqlite_cursor.execute("SELECT COUNT(*) FROM films")
    sqlite_count_before = sqlite_cursor.fetchone()[0]
    print(f"✓ SQLite database currently has {sqlite_count_before} films")
    print()

    # Get all films from PostgreSQL
    print("📦 Reading all films from PostgreSQL...")
    pg_cursor.execute("SELECT * FROM films ORDER BY id")
    pg_films = pg_cursor.fetchall()
    
    # Get column names
    column_names = [desc[0] for desc in pg_cursor.description]
    print(f"✓ Retrieved {len(pg_films)} films from PostgreSQL")
    print(f"✓ Columns: {', '.join(column_names)}")
    print()

    # Ensure SQLite table has all necessary columns
    print("🔧 Ensuring SQLite table has all columns...")
    sqlite_cursor.execute("PRAGMA table_info(films)")
    existing_columns = {row[1] for row in sqlite_cursor.fetchall()}
    
    # Add missing columns
    for col in column_names:
        if col not in existing_columns:
            try:
                if col == 'updated_at' or col == 'created_at':
                    sqlite_cursor.execute(f'ALTER TABLE films ADD COLUMN {col} TIMESTAMP DEFAULT CURRENT_TIMESTAMP')
                elif col == 'a_grade_rank':
                    sqlite_cursor.execute(f'ALTER TABLE films ADD COLUMN {col} INTEGER')
                else:
                    sqlite_cursor.execute(f'ALTER TABLE films ADD COLUMN {col} TEXT')
                print(f"  ✓ Added column: {col}")
            except Exception as e:
                print(f"  ⚠️  Could not add column {col}: {e}")
    
    sqlite_conn.commit()
    print()

    # Clear existing SQLite films
    print("🗑️  Clearing existing SQLite films...")
    sqlite_cursor.execute("DELETE FROM films")
    sqlite_conn.commit()
    print("✓ Cleared SQLite films table")
    print()

    # Insert all films from PostgreSQL into SQLite
    print("⬇️  Syncing films from PostgreSQL to SQLite...")
    inserted = 0

    # Build INSERT statement dynamically based on columns
    placeholders = ', '.join(['?' for _ in column_names])
    columns = ', '.join(column_names)
    
    for film in pg_films:
        sqlite_cursor.execute(f"""
            INSERT INTO films ({columns})
            VALUES ({placeholders})
        """, film)
        inserted += 1
        
        if inserted % 100 == 0:
            print(f"  Processed {inserted}/{len(pg_films)} films...")

    sqlite_conn.commit()
    print(f"✓ Inserted {inserted} films into SQLite")
    print()

    # Verify
    sqlite_cursor.execute("SELECT COUNT(*) FROM films")
    sqlite_count_after = sqlite_cursor.fetchone()[0]

    print("=" * 80)
    print("SYNC COMPLETE!")
    print("=" * 80)
    print(f"PostgreSQL: {pg_count} films")
    print(f"SQLite:     {sqlite_count_before} → {sqlite_count_after} films")
    print(f"Inserted:   {inserted} films")
    print()

    # Show RT score stats
    sqlite_cursor.execute("SELECT COUNT(*) FROM films WHERE rotten_tomatoes IS NOT NULL AND rotten_tomatoes != ''")
    with_rt = sqlite_cursor.fetchone()[0]
    sqlite_cursor.execute("SELECT COUNT(*) FROM films WHERE rotten_tomatoes = 'no RT score'")
    no_rt = sqlite_cursor.fetchone()[0]
    has_score = with_rt - no_rt

    print(f"RT Scores:  {has_score} films ({100*has_score/sqlite_count_after:.1f}%)")
    print(f"No RT:      {no_rt} films marked 'no RT score'")
    print("=" * 80)

    # Close connections
    sqlite_conn.close()
    pg_conn.close()

if __name__ == '__main__':
    main()

