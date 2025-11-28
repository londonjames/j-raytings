import sqlite3
import os
import re
from urllib.parse import urlparse

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

def fix_author_name(author):
    """Convert author name to 'First Last' format, handling multiple authors"""
    if not author:
        return author
    
    # Handle multiple authors separated by & or and
    if ' & ' in author:
        parts = author.split(' & ')
        fixed_parts = []
        for part in parts:
            fixed_parts.append(fix_single_author(part.strip()))
        return ' & '.join(fixed_parts)
    
    if ' and ' in author:
        parts = author.split(' and ')
        fixed_parts = []
        for part in parts:
            fixed_parts.append(fix_single_author(part.strip()))
        return ' and '.join(fixed_parts)
    
    if ';' in author:
        parts = author.split(';')
        fixed_parts = []
        for part in parts:
            fixed_parts.append(fix_single_author(part.strip()))
        return '; '.join(fixed_parts)
    
    # Single author
    return fix_single_author(author)

def fix_single_author(author):
    """Convert a single author from 'Last, First' to 'First Last'"""
    if not author:
        return author
    
    # Check if it's in "Last, First" format
    if ',' in author:
        parts = author.split(',', 1)
        if len(parts) == 2:
            last_name = parts[0].strip()
            first_name = parts[1].strip()
            return f"{first_name} {last_name}"
    
    # Check for incorrectly formatted names like "Steven & Stephen Levitt Dubner"
    # This pattern suggests it was incorrectly converted
    # Pattern: "First1 & First2 Last1 Last2" should be "First1 Last1 & First2 Last2"
    if ' & ' in author and not ',' in author:
        parts = author.split(' & ')
        if len(parts) == 2:
            # Check if this looks like it needs fixing
            # If both parts have multiple words, might be incorrectly formatted
            part1_words = parts[0].strip().split()
            part2_words = parts[1].strip().split()
            
            # If part2 has 2+ words and part1 has 1 word, might be wrong format
            # But this is tricky - let's be conservative and only fix obvious cases
            pass
    
    # If it's already in "First Last" format or doesn't have a comma, return as-is
    return author

def fix_all_author_names():
    """Fix all author names in the database - re-import from original format"""
    # Actually, the best approach is to re-import from the Google Sheet
    # But for now, let's try to fix the obviously wrong ones
    
    conn = get_db()
    cursor = conn.cursor()
    
    # Get all books - we'll need to check the original Google Sheet format
    # For now, let's just re-run the import which will have the correct "Last, First" format
    # and then convert them properly
    
    print("To properly fix author names, we should re-import from Google Sheets")
    print("which has the original 'Last, First' format, then convert them.")
    print("\nAlternatively, we can manually fix the obviously incorrect ones.")
    
    # Let's fix the obvious patterns
    if USE_POSTGRES:
        cursor.execute("SELECT id, author FROM books WHERE author LIKE '% & %' AND author NOT LIKE '%,%'")
    else:
        cursor.execute("SELECT id, author FROM books WHERE author LIKE '% & %' AND author NOT LIKE '%,%'")
    
    potentially_wrong = cursor.fetchall()
    print(f"\nFound {len(potentially_wrong)} authors with '&' but no comma - these might be incorrectly formatted")
    
    conn.close()

if __name__ == '__main__':
    # Actually, let's re-import from Google Sheets to get the original format
    # Then convert properly
    print("The best approach is to:")
    print("1. Re-import books from Google Sheets (which has 'Last, First' format)")
    print("2. Then run the conversion script")
    print("\nOr we can manually fix the database. Let me check what we have...")
    fix_all_author_names()

