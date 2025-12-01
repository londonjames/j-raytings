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
        conn = sqlite3.connect('books.db')
        conn.row_factory = sqlite3.Row
        return conn

def fix_author_name(author):
    """Convert 'Last, First' to 'First Last'"""
    if not author:
        return author
    
    # Handle multiple authors separated by & or and
    # Check for & first (most common)
    if ' & ' in author:
        parts = author.split(' & ')
        fixed_parts = [fix_single_author(part.strip()) for part in parts]
        return ' & '.join(fixed_parts)
    
    # Check for " and " (with spaces)
    if ' and ' in author:
        parts = author.split(' and ')
        fixed_parts = [fix_single_author(part.strip()) for part in parts]
        return ' and '.join(fixed_parts)
    
    # Check for semicolon
    if ';' in author:
        parts = author.split(';')
        fixed_parts = [fix_single_author(part.strip()) for part in parts]
        return '; '.join(fixed_parts)
    
    # Single author
    return fix_single_author(author)

def fix_single_author(author):
    """Convert a single author from 'Last, First' to 'First Last'"""
    if not author:
        return author
    
    # Check if it's in "Last, First" format (most common case)
    if ',' in author:
        parts = author.split(',', 1)
        if len(parts) == 2:
            last_name = parts[0].strip()
            first_name = parts[1].strip()
            # Only convert if it looks like "Last, First" (last name is typically shorter or capitalized)
            # This helps avoid converting things like "Smith, John & Associates"
            if len(last_name.split()) <= 2:  # Last name is usually 1-2 words
                return f"{first_name} {last_name}"
    
    # If it's already in "First Last" format or doesn't have a comma, return as-is
    return author

def fix_all_author_names():
    """Fix all author names in the database"""
    conn = get_db()
    cursor = conn.cursor()
    
    # Get all books with authors
    if USE_POSTGRES:
        cursor.execute("SELECT id, author FROM books WHERE author IS NOT NULL AND author != ''")
    else:
        cursor.execute("SELECT id, author FROM books WHERE author IS NOT NULL AND author != ''")
    
    books = cursor.fetchall()
    
    print(f"Found {len(books)} books with authors")
    print("Fixing author names...\n")
    
    updated_count = 0
    for book in books:
        book_id = book[0] if USE_POSTGRES else book[0]
        old_author = book[1] if USE_POSTGRES else book[1]
        
        new_author = fix_author_name(old_author)
        
        if new_author != old_author:
            print(f"  {old_author} -> {new_author}")
            
            if USE_POSTGRES:
                cursor.execute("UPDATE books SET author = %s WHERE id = %s", (new_author, book_id))
            else:
                cursor.execute("UPDATE books SET author = ? WHERE id = ?", (new_author, book_id))
            
            updated_count += 1
    
    conn.commit()
    conn.close()
    
    print(f"\n✅ Successfully updated {updated_count} author names!")

if __name__ == '__main__':
    fix_all_author_names()

