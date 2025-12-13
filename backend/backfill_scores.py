#!/usr/bin/env python3
"""
Backfill missing scores for all films and books based on their letter_rating/j_rayting
"""
import os
import sys
from urllib.parse import urlparse

# Add parent directory to path to import from app.py
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Import database connection logic from app.py
DATABASE = 'films.db'
DATABASE_URL = os.getenv('DATABASE_URL')
USE_POSTGRES = DATABASE_URL is not None

if USE_POSTGRES:
    import psycopg2
    result = urlparse(DATABASE_URL)
    DB_CONFIG = {
        'dbname': result.path[1:],
        'user': result.username,
        'password': result.password,
        'host': result.hostname,
        'port': result.port
    }
else:
    import sqlite3

def get_db():
    """Get database connection (PostgreSQL or SQLite based on environment)"""
    if USE_POSTGRES:
        conn = psycopg2.connect(**DB_CONFIG)
        return conn
    else:
        conn = sqlite3.connect(DATABASE)
        conn.row_factory = sqlite3.Row
        return conn

def letter_rating_to_score(letter_rating):
    """Convert letter rating to numeric score (out of 20)"""
    if not letter_rating:
        return None
    
    rating_map = {
        'A+': 20,
        'A/A+': 19,
        'A': 18,
        'A-/A': 17,
        'A-': 16,
        'B+/A-': 15,
        'B+': 14,
        'B/B+': 13,
        'B': 12,
        'B-/B': 11,
        'B-': 10,
        'C+/B-': 9,
        'C+': 8,
        'C/C+': 7,
        'C': 6,
        'C-': 5,
        'D+': 4,
        'D': 3,
    }
    
    return rating_map.get(letter_rating.strip())

def backfill_films():
    """Backfill scores for films"""
    conn = get_db()
    cursor = conn.cursor()
    
    # Find films with null or missing scores but have letter_rating
    if USE_POSTGRES:
        cursor.execute('''
            SELECT id, title, letter_rating, score 
            FROM films 
            WHERE (score IS NULL OR score = 0) AND letter_rating IS NOT NULL
        ''')
    else:
        cursor.execute('''
            SELECT id, title, letter_rating, score 
            FROM films 
            WHERE (score IS NULL OR score = 0) AND letter_rating IS NOT NULL
        ''')
    
    films = cursor.fetchall()
    
    if USE_POSTGRES:
        films = [dict(row) for row in films]
    else:
        films = [dict(row) for row in films]
    
    print(f"\n📽️  Found {len(films)} films with missing scores")
    
    updated_count = 0
    skipped_count = 0
    
    for film in films:
        film_id = film['id']
        title = film['title']
        letter_rating = film['letter_rating']
        current_score = film['score']
        
        calculated_score = letter_rating_to_score(letter_rating)
        
        if calculated_score is None:
            print(f"  ⚠️  Skipping '{title}' (ID: {film_id}): Unknown rating '{letter_rating}'")
            skipped_count += 1
            continue
        
        # Update the score
        if USE_POSTGRES:
            cursor.execute('''
                UPDATE films 
                SET score = %s, updated_at = CURRENT_TIMESTAMP 
                WHERE id = %s
            ''', (calculated_score, film_id))
        else:
            cursor.execute('''
                UPDATE films 
                SET score = ?, updated_at = CURRENT_TIMESTAMP 
                WHERE id = ?
            ''', (calculated_score, film_id))
        
        print(f"  ✓ Updated '{title}' (ID: {film_id}): {letter_rating} → {calculated_score}")
        updated_count += 1
    
    conn.commit()
    print(f"\n✅ Updated {updated_count} films, skipped {skipped_count}")
    
    # Check for films with letter_rating but still no score
    if USE_POSTGRES:
        cursor.execute('''
            SELECT COUNT(*) 
            FROM films 
            WHERE (score IS NULL OR score = 0) AND letter_rating IS NOT NULL
        ''')
    else:
        cursor.execute('''
            SELECT COUNT(*) 
            FROM films 
            WHERE (score IS NULL OR score = 0) AND letter_rating IS NOT NULL
        ''')
    
    remaining = cursor.fetchone()[0]
    if remaining > 0:
        print(f"  ⚠️  Warning: {remaining} films still have missing scores")
    
    conn.close()
    return updated_count

def backfill_books():
    """Backfill scores for books"""
    conn = get_db()
    cursor = conn.cursor()
    
    # Find books with null or missing scores but have j_rayting
    if USE_POSTGRES:
        cursor.execute('''
            SELECT id, book_name, author, j_rayting, score 
            FROM books 
            WHERE (score IS NULL OR score = 0) AND j_rayting IS NOT NULL
        ''')
    else:
        cursor.execute('''
            SELECT id, book_name, author, j_rayting, score 
            FROM books 
            WHERE (score IS NULL OR score = 0) AND j_rayting IS NOT NULL
        ''')
    
    books = cursor.fetchall()
    
    if USE_POSTGRES:
        books = [dict(row) for row in books]
    else:
        books = [dict(row) for row in books]
    
    print(f"\n📚 Found {len(books)} books with missing scores")
    
    updated_count = 0
    skipped_count = 0
    
    for book in books:
        book_id = book['id']
        book_name = book['book_name']
        author = book.get('author', 'Unknown')
        j_rayting = book['j_rayting']
        current_score = book['score']
        
        calculated_score = letter_rating_to_score(j_rayting)
        
        if calculated_score is None:
            print(f"  ⚠️  Skipping '{book_name}' by {author} (ID: {book_id}): Unknown rating '{j_rayting}'")
            skipped_count += 1
            continue
        
        # Update the score
        if USE_POSTGRES:
            cursor.execute('''
                UPDATE books 
                SET score = %s, updated_at = CURRENT_TIMESTAMP 
                WHERE id = %s
            ''', (calculated_score, book_id))
        else:
            cursor.execute('''
                UPDATE books 
                SET score = ?, updated_at = CURRENT_TIMESTAMP 
                WHERE id = ?
            ''', (calculated_score, book_id))
        
        print(f"  ✓ Updated '{book_name}' by {author} (ID: {book_id}): {j_rayting} → {calculated_score}")
        updated_count += 1
    
    conn.commit()
    print(f"\n✅ Updated {updated_count} books, skipped {skipped_count}")
    
    # Check for books with j_rayting but still no score
    if USE_POSTGRES:
        cursor.execute('''
            SELECT COUNT(*) 
            FROM books 
            WHERE (score IS NULL OR score = 0) AND j_rayting IS NOT NULL
        ''')
    else:
        cursor.execute('''
            SELECT COUNT(*) 
            FROM books 
            WHERE (score IS NULL OR score = 0) AND j_rayting IS NOT NULL
        ''')
    
    remaining = cursor.fetchone()[0]
    if remaining > 0:
        print(f"  ⚠️  Warning: {remaining} books still have missing scores")
    
    conn.close()
    return updated_count

def verify_all_have_scores():
    """Verify that all entries with ratings have scores"""
    conn = get_db()
    cursor = conn.cursor()
    
    # Check films
    if USE_POSTGRES:
        cursor.execute('''
            SELECT COUNT(*) 
            FROM films 
            WHERE letter_rating IS NOT NULL AND (score IS NULL OR score = 0)
        ''')
    else:
        cursor.execute('''
            SELECT COUNT(*) 
            FROM films 
            WHERE letter_rating IS NOT NULL AND (score IS NULL OR score = 0)
        ''')
    
    films_missing = cursor.fetchone()[0]
    
    # Check books
    if USE_POSTGRES:
        cursor.execute('''
            SELECT COUNT(*) 
            FROM books 
            WHERE j_rayting IS NOT NULL AND (score IS NULL OR score = 0)
        ''')
    else:
        cursor.execute('''
            SELECT COUNT(*) 
            FROM books 
            WHERE j_rayting IS NOT NULL AND (score IS NULL OR score = 0)
        ''')
    
    books_missing = cursor.fetchone()[0]
    
    conn.close()
    
    print("\n" + "=" * 80)
    print("VERIFICATION SUMMARY")
    print("=" * 80)
    print(f"📽️  Films with rating but missing score: {films_missing}")
    print(f"📚 Books with rating but missing score: {books_missing}")
    
    if films_missing == 0 and books_missing == 0:
        print("\n✅ SUCCESS: All entries with ratings now have scores!")
        return True
    else:
        print(f"\n⚠️  WARNING: {films_missing + books_missing} entries still need scores")
        return False

def main():
    print("=" * 80)
    print("BACKFILLING SCORES FOR FILMS AND BOOKS")
    print("=" * 80)
    print(f"Database: {'PostgreSQL' if USE_POSTGRES else 'SQLite'}")
    
    # Backfill films
    films_updated = backfill_films()
    
    # Backfill books
    books_updated = backfill_books()
    
    # Verify
    all_good = verify_all_have_scores()
    
    print("\n" + "=" * 80)
    print("BACKFILL COMPLETE")
    print("=" * 80)
    print(f"Total films updated: {films_updated}")
    print(f"Total books updated: {books_updated}")
    
    if not all_good:
        sys.exit(1)

if __name__ == '__main__':
    main()

