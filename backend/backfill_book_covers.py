#!/usr/bin/env python3
"""
Script to backfill missing book cover images from Google Books API
"""
import sqlite3
import os
import time
from google_books_service import search_book

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

def backfill_covers():
    """Backfill missing book covers"""
    conn = get_db()
    cursor = conn.cursor()
    
    # Get books without covers
    if USE_POSTGRES:
        cursor.execute('''
            SELECT id, book_name, author, google_books_id 
            FROM books 
            WHERE cover_url IS NULL OR cover_url = '' OR cover_url = 'PLACEHOLDER'
            ORDER BY id
        ''')
    else:
        cursor.execute('''
            SELECT id, book_name, author, google_books_id 
            FROM books 
            WHERE cover_url IS NULL OR cover_url = '' OR cover_url = 'PLACEHOLDER'
            ORDER BY id
        ''')
    
    books_without_covers = cursor.fetchall()
    total = len(books_without_covers)
    
    print(f"Found {total} books without covers\n")
    
    if total == 0:
        print("All books have covers!")
        conn.close()
        return
    
    success_count = 0
    failed_count = 0
    
    for i, book in enumerate(books_without_covers, 1):
        book_id = book[0]
        book_name = book[1]
        author = book[2]
        existing_gb_id = book[3] if len(book) > 3 else None
        
        print(f"[{i}/{total}] Searching for '{book_name}' by {author or 'Unknown'}...")
        
        # Try searching
        book_data = search_book(book_name, author)
        
        if book_data and book_data.get('cover_url'):
            cover_url = book_data['cover_url']
            google_books_id = book_data.get('google_books_id') or existing_gb_id
            
            # Update database
            if USE_POSTGRES:
                cursor.execute(
                    'UPDATE books SET cover_url = %s, google_books_id = %s WHERE id = %s',
                    (cover_url, google_books_id, book_id)
                )
            else:
                cursor.execute(
                    'UPDATE books SET cover_url = ?, google_books_id = ? WHERE id = ?',
                    (cover_url, google_books_id, book_id)
                )
            
            conn.commit()
            success_count += 1
            print(f"  ✓ Found and updated cover")
        else:
            failed_count += 1
            print(f"  ✗ No cover found")
        
        # Rate limiting - Google Books allows 1000 requests/day free tier
        if i < total:
            time.sleep(0.25)  # 250ms delay between requests
    
    conn.close()
    
    print(f"\n✓ Successfully updated {success_count} covers")
    print(f"✗ Failed to find covers for {failed_count} books")

if __name__ == '__main__':
    backfill_covers()

