#!/usr/bin/env python3
"""
Sync PostgreSQL production database to SQLite local database (BOOKS)
This will REPLACE local book data with production data to ensure local matches production
PRODUCTION IS THE SOURCE OF TRUTH - all production data will be synced to local
"""
import sqlite3
import psycopg2
from urllib.parse import urlparse
import os

# PostgreSQL connection string
DATABASE_URL = os.getenv('DATABASE_URL') or "postgresql://postgres:rcvXfFuoGQZokshoQKRJvMcZGvvweTHI@gondola.proxy.rlwy.net:57791/railway"

def main():
    print("=" * 80)
    print("SYNCING POSTGRESQL TO SQLITE (BOOKS)")
    print("=" * 80)
    print()
    print("⚠️  WARNING: This will REPLACE all local book data with production data!")
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

    # Ensure books table exists in PostgreSQL
    pg_cursor.execute("SELECT COUNT(*) FROM books")
    pg_count = pg_cursor.fetchone()[0]
    print(f"✓ PostgreSQL database has {pg_count} books")
    print()

    # Connect to SQLite
    print("📂 Connecting to local SQLite database...")
    sqlite_conn = sqlite3.connect('films.db')
    sqlite_cursor = sqlite_conn.cursor()

    # Ensure books table exists in SQLite
    sqlite_cursor.execute('''
        CREATE TABLE IF NOT EXISTS books (
            id INTEGER PRIMARY KEY,
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
            notion_link TEXT,
            cover_url TEXT,
            google_books_id TEXT,
            isbn TEXT,
            average_rating REAL,
            ratings_count INTEGER,
            published_date TEXT,
            year_written INTEGER,
            description TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')

    # Get count from SQLite before
    sqlite_cursor.execute("SELECT COUNT(*) FROM books")
    sqlite_count_before = sqlite_cursor.fetchone()[0]
    print(f"✓ SQLite database currently has {sqlite_count_before} books")
    print()

    # Get all books from PostgreSQL
    print("📦 Reading all books from PostgreSQL...")
    pg_cursor.execute("SELECT * FROM books ORDER BY id")
    pg_books = pg_cursor.fetchall()
    
    # Get column names
    column_names = [desc[0] for desc in pg_cursor.description]
    print(f"✓ Retrieved {len(pg_books)} books from PostgreSQL")
    print(f"✓ Columns: {', '.join(column_names)}")
    print()

    # Ensure SQLite table has all necessary columns
    print("🔧 Ensuring SQLite table has all columns...")
    sqlite_cursor.execute("PRAGMA table_info(books)")
    existing_columns = {row[1] for row in sqlite_cursor.fetchall()}
    
    # Add missing columns
    for col in column_names:
        if col not in existing_columns:
            try:
                if col == 'updated_at' or col == 'created_at':
                    # SQLite doesn't support DEFAULT CURRENT_TIMESTAMP in ALTER TABLE, add without default
                    sqlite_cursor.execute(f'ALTER TABLE books ADD COLUMN {col} TIMESTAMP')
                elif col in ['id', 'order_number', 'year', 'score', 'pages', 'ratings_count', 'year_written', 'a_grade_rank']:
                    sqlite_cursor.execute(f'ALTER TABLE books ADD COLUMN {col} INTEGER')
                elif col == 'average_rating':
                    sqlite_cursor.execute(f'ALTER TABLE books ADD COLUMN {col} REAL')
                else:
                    sqlite_cursor.execute(f'ALTER TABLE books ADD COLUMN {col} TEXT')
                print(f"  ✓ Added column: {col}")
            except Exception as e:
                print(f"  ⚠️  Could not add column {col}: {e}")
    
    sqlite_conn.commit()
    print()

    # Clear existing SQLite books
    print("🗑️  Clearing existing SQLite books...")
    sqlite_cursor.execute("DELETE FROM books")
    sqlite_conn.commit()
    print("✓ Cleared SQLite books table")
    print()

    # Insert all books from PostgreSQL into SQLite
    print("⬇️  Syncing books from PostgreSQL to SQLite...")
    inserted = 0

    # Use all columns from PostgreSQL
    placeholders = ', '.join(['?' for _ in column_names])
    columns = ', '.join(column_names)
    
    for book in pg_books:
        sqlite_cursor.execute(f"""
            INSERT INTO books ({columns})
            VALUES ({placeholders})
        """, book)
        inserted += 1
        
        if inserted % 100 == 0:
            print(f"  Processed {inserted}/{len(pg_books)} books...")

    sqlite_conn.commit()
    print(f"✓ Inserted {inserted} books into SQLite")
    print()

    # Verify
    sqlite_cursor.execute("SELECT COUNT(*) FROM books")
    sqlite_count_after = sqlite_cursor.fetchone()[0]

    print("=" * 80)
    print("SYNC COMPLETE!")
    print("=" * 80)
    print(f"PostgreSQL: {pg_count} books")
    print(f"SQLite:     {sqlite_count_before} → {sqlite_count_after} books")
    print(f"Inserted:   {inserted} books")
    print("=" * 80)

    # Close connections
    sqlite_conn.close()
    pg_conn.close()

if __name__ == '__main__':
    main()

