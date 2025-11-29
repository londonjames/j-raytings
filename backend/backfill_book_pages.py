#!/usr/bin/env python3
"""
Script to backfill missing book page numbers from Google Books API
"""
import sqlite3
import os
import time
from google_books_service import search_book, get_book_details

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

def backfill_pages():
    """Backfill missing book page numbers"""
    conn = get_db()
    cursor = conn.cursor()
    
    # Get books without page numbers (NULL, 0, or empty)
    if USE_POSTGRES:
        cursor.execute('''
            SELECT id, book_name, author, google_books_id 
            FROM books 
            WHERE pages IS NULL OR pages = 0 OR pages = ''
            ORDER BY id
        ''')
    else:
        cursor.execute('''
            SELECT id, book_name, author, google_books_id 
            FROM books 
            WHERE pages IS NULL OR pages = 0 OR pages = ''
            ORDER BY id
        ''')
    
    books_without_pages = cursor.fetchall()
    total = len(books_without_pages)
    
    print(f"Found {total} books without page numbers\n")
    
    if total == 0:
        print("All books have page numbers!")
        conn.close()
        return
    
    success_count = 0
    failed_count = 0
    
    for i, book in enumerate(books_without_pages, 1):
        book_id = book[0]
        book_name = book[1]
        author = book[2]
        existing_gb_id = book[3] if len(book) > 3 else None
        
        print(f"[{i}/{total}] Searching for '{book_name}' by {author or 'Unknown'}...")
        
        book_data = None
        
        # If we have a google_books_id, use get_book_details (more reliable)
        if existing_gb_id:
            book_data = get_book_details(existing_gb_id)
            if not book_data:
                # Fallback to search if get_book_details fails
                book_data = search_book(book_name, author)
        else:
            # Search by title and author
            book_data = search_book(book_name, author)
        
        if book_data and book_data.get('page_count'):
            page_count = book_data['page_count']
            
            # Update database
            if USE_POSTGRES:
                cursor.execute(
                    'UPDATE books SET pages = %s WHERE id = %s',
                    (page_count, book_id)
                )
            else:
                cursor.execute(
                    'UPDATE books SET pages = ? WHERE id = ?',
                    (page_count, book_id)
                )
            
            conn.commit()
            success_count += 1
            print(f"  ✓ Found and updated: {page_count} pages")
        else:
            failed_count += 1
            print(f"  ✗ No page count found")
        
        # Rate limiting - Google Books allows 1000 requests/day free tier
        if i < total:
            time.sleep(0.25)  # 250ms delay between requests
    
    conn.close()
    
    print(f"\n✓ Successfully updated {success_count} books with page numbers")
    print(f"✗ Failed to find page numbers for {failed_count} books")

if __name__ == '__main__':
    backfill_pages()

