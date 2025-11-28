import sqlite3
import os
from urllib.parse import urlparse

# Detect if we should use PostgreSQL or SQLite
DATABASE_URL = os.getenv('DATABASE_URL')
USE_POSTGRES = DATABASE_URL is not None

if USE_POSTGRES:
    import psycopg2
    from urllib.parse import urlparse
    
    # Parse DATABASE_URL for psycopg2
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

def fix_book_titles():
    """Fix book titles that end with ', The' to start with 'The '"""
    conn = get_db()
    cursor = conn.cursor()
    
    # Find all books with titles ending in ", The"
    if USE_POSTGRES:
        cursor.execute("SELECT id, book_name FROM books WHERE book_name LIKE '%, The'")
    else:
        cursor.execute("SELECT id, book_name FROM books WHERE book_name LIKE '%, The'")
    
    books_to_fix = cursor.fetchall()
    
    print(f"Found {len(books_to_fix)} books to fix:")
    
    updated_count = 0
    for book in books_to_fix:
        book_id = book[0] if USE_POSTGRES else book[0]
        old_name = book[1] if USE_POSTGRES else book[1]
        
        # Transform "Right Stuff, The" -> "The Right Stuff"
        if old_name.endswith(', The'):
            new_name = 'The ' + old_name[:-5]  # Remove ', The' and add 'The ' at the beginning
            print(f"  {old_name} -> {new_name}")
            
            if USE_POSTGRES:
                cursor.execute("UPDATE books SET book_name = %s WHERE id = %s", (new_name, book_id))
            else:
                cursor.execute("UPDATE books SET book_name = ? WHERE id = ?", (new_name, book_id))
            
            updated_count += 1
    
    conn.commit()
    conn.close()
    
    print(f"\n✅ Successfully updated {updated_count} book titles!")

if __name__ == '__main__':
    fix_book_titles()

