#!/usr/bin/env python3
"""
Sync books from SQLite database to PostgreSQL production database
This will replace all books data in PostgreSQL with the updated SQLite data
"""
import sqlite3
import psycopg2
from urllib.parse import urlparse
import os

# PostgreSQL connection string (use environment variable if available)
DATABASE_URL = os.getenv('DATABASE_URL') or "postgresql://postgres:rcvXfFuoGQZokshoQKRJvMcZGvvweTHI@gondola.proxy.rlwy.net:57791/railway"

def main():
    print("=" * 80)
    print("SYNCING BOOKS FROM SQLITE TO POSTGRESQL")
    print("=" * 80)
    print()

    # Connect to SQLite
    print("📂 Connecting to local SQLite database...")
    sqlite_conn = sqlite3.connect('films.db')
    sqlite_conn.row_factory = sqlite3.Row
    sqlite_cursor = sqlite_conn.cursor()

    # Get count from SQLite
    sqlite_cursor.execute("SELECT COUNT(*) FROM books")
    sqlite_count = sqlite_cursor.fetchone()[0]
    print(f"✓ SQLite database has {sqlite_count} books")
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

    # Ensure books table exists
    print("📚 Ensuring books table exists...")
    pg_cursor.execute('''
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
                notion_link TEXT,
                cover_url TEXT,
                google_books_id TEXT,
                isbn TEXT,
                average_rating REAL,
                ratings_count INTEGER,
                published_date TEXT,
                year_written INTEGER,
                description TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
    ''')
    
        # Add missing columns if they don't exist
        for column_name, column_type in [
            ('cover_url', 'TEXT'), ('google_books_id', 'TEXT'), ('isbn', 'TEXT'),
            ('average_rating', 'REAL'), ('ratings_count', 'INTEGER'),
            ('published_date', 'TEXT'), ('year_written', 'INTEGER'), ('description', 'TEXT'),
            ('notion_link', 'TEXT')
        ]:
        pg_cursor.execute("""
            SELECT column_name 
            FROM information_schema.columns 
            WHERE table_name='books' AND column_name=%s
        """, (column_name,))
        if not pg_cursor.fetchone():
            try:
                pg_cursor.execute(f'ALTER TABLE books ADD COLUMN {column_name} {column_type}')
                print(f"  ✓ Added {column_name} column")
            except Exception as e:
                print(f"  ⚠️  Error adding {column_name} column: {e}")
    
    pg_conn.commit()

    # Get count from PostgreSQL before
    pg_cursor.execute("SELECT COUNT(*) FROM books")
    pg_count_before = pg_cursor.fetchone()[0]
    print(f"✓ PostgreSQL currently has {pg_count_before} books")
    print()

    # Clear PostgreSQL table
    print("🗑️  Clearing PostgreSQL books table...")
    pg_cursor.execute("DELETE FROM books")
    pg_conn.commit()
    print("✓ Cleared all existing data")
    print()

    # Get all books from SQLite
    print("📦 Reading all books from SQLite...")
    sqlite_cursor.execute("SELECT * FROM books ORDER BY id")
    books = sqlite_cursor.fetchall()
    print(f"✓ Retrieved {len(books)} books")
    print()

    # Insert into PostgreSQL
    print("⬆️  Uploading books to PostgreSQL...")
    inserted = 0

    for book in books:
        # Helper function to safely get values from Row object
        def get_value(key, default=None):
            try:
                return book[key]
            except (KeyError, IndexError):
                return default
        
        pg_cursor.execute("""
            INSERT INTO books (
                id, order_number, date_read, year, book_name, author,
                details_commentary, j_rayting, score, type, pages, form,
                notes_in_notion, notion_link, cover_url, google_books_id, isbn,
                average_rating, ratings_count, published_date, year_written, description
            ) VALUES (
                %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s
            )
        """, (
            get_value('id'),
            get_value('order_number'),
            get_value('date_read'),
            get_value('year'),
            get_value('book_name'),
            get_value('author'),
            get_value('details_commentary'),
            get_value('j_rayting'),
            get_value('score'),
            get_value('type'),
            get_value('pages'),
            get_value('form'),
            get_value('notes_in_notion'),
            get_value('notion_link'),
            get_value('cover_url'),
            get_value('google_books_id'),
            get_value('isbn'),
            get_value('average_rating'),
            get_value('ratings_count'),
            get_value('published_date'),
            get_value('year_written'),
            get_value('description')
        ))
        inserted += 1

        if inserted % 100 == 0:
            print(f"  Uploaded {inserted}/{len(books)} books...")

    pg_conn.commit()
    print(f"✓ Successfully uploaded {inserted} books")
    print()

    # Reset sequence
    print("🔧 Resetting ID sequence...")
    pg_cursor.execute("SELECT MAX(id) FROM books")
    max_id = pg_cursor.fetchone()[0]
    if max_id:
        pg_cursor.execute(f"SELECT setval('books_id_seq', {max_id})")
        pg_conn.commit()
        print(f"✓ Sequence reset to {max_id}")
    print()

    # Verify
    pg_cursor.execute("SELECT COUNT(*) FROM books")
    pg_count_after = pg_cursor.fetchone()[0]

    print("=" * 80)
    print("SYNC COMPLETE!")
    print("=" * 80)
    print(f"SQLite:     {sqlite_count} books")
    print(f"PostgreSQL: {pg_count_after} books")
    print(f"Difference: {pg_count_before - pg_count_after} books removed")
    print()

    # Show cover stats
    pg_cursor.execute("SELECT COUNT(*) FROM books WHERE cover_url IS NOT NULL AND cover_url != '' AND cover_url != 'PLACEHOLDER'")
    with_covers = pg_cursor.fetchone()[0]
    pg_cursor.execute("SELECT COUNT(*) FROM books WHERE published_date IS NOT NULL AND published_date != ''")
    with_dates = pg_cursor.fetchone()[0]
    pg_cursor.execute("SELECT COUNT(*) FROM books WHERE year_written IS NOT NULL")
    with_year_written = pg_cursor.fetchone()[0]

    print(f"Covers:     {with_covers} books ({100*with_covers/pg_count_after:.1f}%)")
    print(f"Published dates: {with_dates} books ({100*with_dates/pg_count_after:.1f}%)")
    print(f"Year written: {with_year_written} books ({100*with_year_written/pg_count_after:.1f}%)")
    print("=" * 80)

    # Close connections
    sqlite_conn.close()
    pg_conn.close()

if __name__ == '__main__':
    main()

