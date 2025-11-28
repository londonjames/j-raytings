import sqlite3
import os
import time
from urllib.parse import urlparse
from open_library_service import get_book_rating_by_isbn, get_book_rating_by_title_author

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
    """Get database connection (PostgreSQL or SQLite based on environment)"""
    if USE_POSTGRES:
        conn = psycopg2.connect(**DB_CONFIG)
        return conn
    else:
        conn = sqlite3.connect('films.db')
        conn.row_factory = sqlite3.Row
        return conn

def backfill_ratings():
    """Backfill ratings from Open Library for books that don't have ratings"""
    conn = get_db()
    if USE_POSTGRES:
        cursor = conn.cursor()
        cursor.execute("SELECT id, book_name, author, isbn FROM books WHERE average_rating IS NULL ORDER BY id")
    else:
        cursor = conn.cursor()
        cursor.execute("SELECT id, book_name, author, isbn FROM books WHERE average_rating IS NULL ORDER BY id")
    
    books_without_ratings = cursor.fetchall()
    
    print(f"Found {len(books_without_ratings)} books without ratings")
    print("Attempting to fetch ratings from Open Library...\n")
    
    updated_count = 0
    for i, book in enumerate(books_without_ratings):
        book_id = book[0] if USE_POSTGRES else book[0]
        book_name = book[1] if USE_POSTGRES else book[1]
        author = book[2] if USE_POSTGRES else book[2]
        isbn = book[3] if USE_POSTGRES else book[3]
        
        print(f"[{i+1}/{len(books_without_ratings)}] Checking '{book_name}' by {author or 'Unknown'}...")
        
        rating_data = None
        
        # Try ISBN first if available
        if isbn:
            rating_data = get_book_rating_by_isbn(isbn)
        
        # Fallback to title/author search
        if not rating_data:
            rating_data = get_book_rating_by_title_author(book_name, author)
        
        if rating_data and rating_data.get('average_rating'):
            average_rating = rating_data.get('average_rating')
            ratings_count = rating_data.get('ratings_count', 0)
            
            print(f"  ✓ Found rating: {average_rating} ({ratings_count} ratings)")
            
            if USE_POSTGRES:
                cursor.execute(
                    "UPDATE books SET average_rating = %s, ratings_count = %s WHERE id = %s",
                    (average_rating, ratings_count, book_id)
                )
            else:
                cursor.execute(
                    "UPDATE books SET average_rating = ?, ratings_count = ? WHERE id = ?",
                    (average_rating, ratings_count, book_id)
                )
            
            updated_count += 1
        else:
            print(f"  ✗ No rating found")
        
        # Rate limiting - be respectful to Open Library
        if i < len(books_without_ratings) - 1:
            time.sleep(0.5)  # Small delay between requests
        
        # Commit every 10 books
        if (i + 1) % 10 == 0:
            conn.commit()
            print(f"\n  Committed {i+1} books...\n")
    
    conn.commit()
    conn.close()
    
    print(f"\n✅ Successfully updated {updated_count} books with ratings from Open Library!")
    print(f"   {len(books_without_ratings) - updated_count} books still without ratings")

if __name__ == '__main__':
    backfill_ratings()

