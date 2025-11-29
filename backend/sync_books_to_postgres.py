#!/usr/bin/env python3
"""
Sync books from SQLite database to PostgreSQL production database
This will MERGE data - preserving books added in production while updating/inserting from SQLite
PRODUCTION IS THE SOURCE OF TRUTH - books added in production will be preserved
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

    # Get all books from SQLite
    print("📦 Reading all books from SQLite...")
    sqlite_cursor.execute("SELECT * FROM books ORDER BY id")
    sqlite_books = sqlite_cursor.fetchall()
    print(f"✓ Retrieved {len(sqlite_books)} books from SQLite")
    print()

    # Get existing books from PostgreSQL (to preserve ones added in production)
    print("📦 Reading existing books from PostgreSQL...")
    pg_cursor.execute("SELECT id, book_name, author FROM books")
    pg_existing_books = {row[0]: (row[1], row[2]) for row in pg_cursor.fetchall()}
    print(f"✓ Found {len(pg_existing_books)} existing books in PostgreSQL")
    print()

    # Helper function to safely get values from Row object
    def get_value(book, key, default=None):
        try:
            return book[key]
        except (KeyError, IndexError):
            return default

    # Update or insert books from SQLite
    print("⬆️  Syncing books from SQLite to PostgreSQL...")
    updated = 0
    inserted = 0
    preserved = 0

    for book in sqlite_books:
        book_id = get_value(book, 'id')
        
        # Check if book exists in PostgreSQL
        pg_cursor.execute("SELECT id FROM books WHERE id = %s", (book_id,))
        exists = pg_cursor.fetchone()
        
        if exists:
            # Update existing book
            pg_cursor.execute("""
                UPDATE books SET
                    order_number = %s, date_read = %s, year = %s, book_name = %s, author = %s,
                    details_commentary = %s, j_rayting = %s, score = %s, type = %s, pages = %s, form = %s,
                    notes_in_notion = %s, notion_link = %s, cover_url = %s, google_books_id = %s, isbn = %s,
                    average_rating = %s, ratings_count = %s, published_date = %s, year_written = %s, description = %s
                WHERE id = %s
            """, (
                get_value(book, 'order_number'),
                get_value(book, 'date_read'),
                get_value(book, 'year'),
                get_value(book, 'book_name'),
                get_value(book, 'author'),
                get_value(book, 'details_commentary'),
                get_value(book, 'j_rayting'),
                get_value(book, 'score'),
                get_value(book, 'type'),
                get_value(book, 'pages'),
                get_value(book, 'form'),
                get_value(book, 'notes_in_notion'),
                get_value(book, 'notion_link'),
                get_value(book, 'cover_url'),
                get_value(book, 'google_books_id'),
                get_value(book, 'isbn'),
                get_value(book, 'average_rating'),
                get_value(book, 'ratings_count'),
                get_value(book, 'published_date'),
                get_value(book, 'year_written'),
                get_value(book, 'description'),
                book_id
            ))
            updated += 1
        else:
            # Insert new book
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
                book_id,
                get_value(book, 'order_number'),
                get_value(book, 'date_read'),
                get_value(book, 'year'),
                get_value(book, 'book_name'),
                get_value(book, 'author'),
                get_value(book, 'details_commentary'),
                get_value(book, 'j_rayting'),
                get_value(book, 'score'),
                get_value(book, 'type'),
                get_value(book, 'pages'),
                get_value(book, 'form'),
                get_value(book, 'notes_in_notion'),
                get_value(book, 'notion_link'),
                get_value(book, 'cover_url'),
                get_value(book, 'google_books_id'),
                get_value(book, 'isbn'),
                get_value(book, 'average_rating'),
                get_value(book, 'ratings_count'),
                get_value(book, 'published_date'),
                get_value(book, 'year_written'),
                get_value(book, 'description')
            ))
            inserted += 1

        if (updated + inserted) % 100 == 0:
            print(f"  Processed {updated + inserted}/{len(sqlite_books)} books...")

    pg_conn.commit()
    
    # Count books that exist in PostgreSQL but not SQLite (preserved production entries)
    pg_cursor.execute("SELECT COUNT(*) FROM books WHERE id NOT IN (SELECT id FROM (SELECT id FROM books) AS pg_ids)")
    # Better approach: get all PG IDs and check against SQLite
    pg_cursor.execute("SELECT id FROM books")
    pg_all_ids = {row[0] for row in pg_cursor.fetchall()}
    sqlite_all_ids = {get_value(book, 'id') for book in sqlite_books}
    preserved_ids = pg_all_ids - sqlite_all_ids
    preserved = len(preserved_ids)
    
    print(f"✓ Updated {updated} existing books")
    print(f"✓ Inserted {inserted} new books from SQLite")
    print(f"✓ Preserved {preserved} books that exist only in PostgreSQL (added in production)")
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
    print(f"Updated:    {updated} books")
    print(f"Inserted:   {inserted} books from SQLite")
    print(f"Preserved:  {preserved} books from production (not in SQLite)")
    print()

    # Show cover stats
    pg_cursor.execute("SELECT COUNT(*) FROM books WHERE cover_url IS NOT NULL AND cover_url != '' AND cover_url != 'PLACEHOLDER'")
    with_covers = pg_cursor.fetchone()[0]
    pg_cursor.execute("SELECT COUNT(*) FROM books WHERE published_date IS NOT NULL AND published_date != ''")
    with_dates = pg_cursor.fetchone()[0]
    pg_cursor.execute("SELECT COUNT(*) FROM books WHERE year_written IS NOT NULL")
    with_year_written = pg_cursor.fetchone()[0]
    pg_cursor.execute("SELECT COUNT(*) FROM books WHERE pages IS NOT NULL AND pages > 0")
    with_pages = pg_cursor.fetchone()[0]

    print(f"Covers:     {with_covers} books ({100*with_covers/pg_count_after:.1f}%)")
    print(f"Published dates: {with_dates} books ({100*with_dates/pg_count_after:.1f}%)")
    print(f"Year written: {with_year_written} books ({100*with_year_written/pg_count_after:.1f}%)")
    print(f"Page numbers: {with_pages} books ({100*with_pages/pg_count_after:.1f}%)")
    print("=" * 80)

    # Close connections
    sqlite_conn.close()
    pg_conn.close()

if __name__ == '__main__':
    main()

