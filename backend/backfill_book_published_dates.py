#!/usr/bin/env python3
"""
Script to backfill missing published_date for books from Google Books API
"""
import sqlite3
import os
import time
from google_books_service import get_book_details, search_book

DATABASE = 'films.db'

# Detect if we should use PostgreSQL or SQLite
DATABASE_URL = os.getenv('DATABASE_URL')
USE_POSTGRES = DATABASE_URL is not None

if USE_POSTGRES:
    import psycopg2
    from urllib.parse import urlparse
    
    result = urlparse(DATABASE_URL)
    DB_CONFIG = {
        'dbname': result.path[1:],
        'user': result.username,
        'password': result.password,
        'host': result.hostname,
        'port': result.port
    }

def get_db():
    """Get database connection"""
    if USE_POSTGRES:
        conn = psycopg2.connect(**DB_CONFIG)
        return conn
    else:
        conn = sqlite3.connect(DATABASE, timeout=30.0)
        conn.row_factory = sqlite3.Row
        return conn

def backfill_published_dates():
    """Backfill missing published dates"""
    conn = get_db()
    cursor = conn.cursor()
    
    # Get books without published_date
    if USE_POSTGRES:
        cursor.execute('''
            SELECT id, book_name, author, google_books_id 
            FROM books 
            WHERE published_date IS NULL OR published_date = ''
            ORDER BY id
        ''')
    else:
        cursor.execute('''
            SELECT id, book_name, author, google_books_id 
            FROM books 
            WHERE published_date IS NULL OR published_date = ''
            ORDER BY id
        ''')
    
    books_without_date = cursor.fetchall()
    total = len(books_without_date)
    
    print(f"Found {total} books without published_date\n")
    
    if total == 0:
        print("All books have published dates!")
        conn.close()
        return
    
    success_count = 0
    failed_count = 0
    
    for i, book in enumerate(books_without_date, 1):
        book_id = book[0]
        book_name = book[1]
        author = book[2]
        google_books_id = book[3] if len(book) > 3 else None
        
        print(f"[{i}/{total}] '{book_name}' by {author or 'Unknown'}...")
        
        published_date = None
        
        # Strategy 1: If we have google_books_id, use it to get details
        if google_books_id:
            print(f"  Using Google Books ID: {google_books_id}")
            book_data = get_book_details(google_books_id)
            if book_data and book_data.get('published_date'):
                published_date = book_data['published_date']
        
        # Strategy 2: If that didn't work, search for the book
        if not published_date:
            print(f"  Searching Google Books...")
            book_data = search_book(book_name, author)
            if book_data:
                published_date = book_data.get('published_date')
                # Also update google_books_id if we got one
                if book_data.get('google_books_id') and not google_books_id:
                    google_books_id = book_data['google_books_id']
        
        if published_date:
            # Update database
            if USE_POSTGRES:
                if google_books_id:
                    cursor.execute(
                        'UPDATE books SET published_date = %s, google_books_id = %s WHERE id = %s',
                        (published_date, google_books_id, book_id)
                    )
                else:
                    cursor.execute(
                        'UPDATE books SET published_date = %s WHERE id = %s',
                        (published_date, book_id)
                    )
            else:
                if google_books_id:
                    cursor.execute(
                        'UPDATE books SET published_date = ?, google_books_id = ? WHERE id = ?',
                        (published_date, google_books_id, book_id)
                    )
                else:
                    cursor.execute(
                        'UPDATE books SET published_date = ? WHERE id = ?',
                        (published_date, book_id)
                    )
            
            conn.commit()
            success_count += 1
            print(f"  ✓ Found published_date: {published_date}")
        else:
            failed_count += 1
            print(f"  ✗ No published_date found")
        
        # Rate limiting
        if i < total:
            time.sleep(0.25)  # 250ms delay between requests
    
    conn.close()
    
    print(f"\n✓ Successfully updated {success_count} published dates")
    print(f"✗ Failed to find published dates for {failed_count} books")

if __name__ == '__main__':
    backfill_published_dates()

