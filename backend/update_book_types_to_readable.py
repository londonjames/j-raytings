#!/usr/bin/env python3
"""
Update book types from old format (NF/SPORT, FICT, etc.) to new readable format
(Non-fiction: Sport, Fiction, etc.)
"""
import os
import sqlite3
from urllib.parse import urlparse

# Detect if we should use PostgreSQL or SQLite
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

def get_db():
    """Get database connection"""
    if USE_POSTGRES:
        conn = psycopg2.connect(**DB_CONFIG)
        return conn
    else:
        conn = sqlite3.connect('books.db')
        conn.row_factory = sqlite3.Row
        return conn

# Mapping from old format to new format
TYPE_MAPPING = {
    'FICT': 'Fiction',
    'Fiction': 'Fiction',  # Already correct
    'NF/BIO': 'Non-fiction: Bio',
    'NF/BUSIN': 'Non-fiction: Business',
    'NF/POL': 'Non-fiction: Politics',
    'NF/SOC': 'Non-fiction: Social',
    'NF/SPORT': 'Non-fiction: Sport',
    'NF/TRUECRIME': 'Non-fiction: True Crime',
    'NON-FICT': 'Non-fiction',  # Generic non-fiction
    'Non-fiction: Social': 'Non-fiction: Social',  # Already correct
    'Non-fiction: Sport': 'Non-fiction: Sport',  # Already correct
}

def main():
    print("=" * 80)
    print("UPDATING BOOK TYPES TO READABLE FORMAT")
    print("=" * 80)
    print()
    
    conn = get_db()
    cursor = conn.cursor()
    
    # Get all unique types
    if USE_POSTGRES:
        cursor.execute("SELECT DISTINCT type FROM books WHERE type IS NOT NULL ORDER BY type")
    else:
        cursor.execute("SELECT DISTINCT type FROM books WHERE type IS NOT NULL ORDER BY type")
    
    current_types = [row[0] if USE_POSTGRES else row['type'] for row in cursor.fetchall()]
    print(f"Found {len(current_types)} unique book types:")
    for t in current_types:
        print(f"  - {t}")
    print()
    
    updated_count = 0
    skipped_count = 0
    
    print("Updating book types...")
    for old_type, new_type in TYPE_MAPPING.items():
        if old_type == new_type:
            continue  # Skip if already correct
        
        # Count how many books have this type
        if USE_POSTGRES:
            cursor.execute("SELECT COUNT(*) FROM books WHERE type = %s", (old_type,))
        else:
            cursor.execute("SELECT COUNT(*) FROM books WHERE type = ?", (old_type,))
        
        count = cursor.fetchone()[0] if USE_POSTGRES else cursor.fetchone()['COUNT(*)']
        
        if count > 0:
            # Update all books with this type
            if USE_POSTGRES:
                cursor.execute("UPDATE books SET type = %s WHERE type = %s", (new_type, old_type))
            else:
                cursor.execute("UPDATE books SET type = ? WHERE type = ?", (new_type, old_type))
            
            print(f"  ✓ {old_type} → {new_type} ({count} books)")
            updated_count += count
        else:
            skipped_count += 1
    
    conn.commit()
    
    # Show final types
    if USE_POSTGRES:
        cursor.execute("SELECT DISTINCT type FROM books WHERE type IS NOT NULL ORDER BY type")
    else:
        cursor.execute("SELECT DISTINCT type FROM books WHERE type IS NOT NULL ORDER BY type")
    
    final_types = [row[0] if USE_POSTGRES else row['type'] for row in cursor.fetchall()]
    
    conn.close()
    
    print()
    print("=" * 80)
    print(f"✅ UPDATE COMPLETE")
    print("=" * 80)
    print(f"Updated: {updated_count} books")
    print(f"Skipped: {skipped_count} type mappings (not found)")
    print()
    print(f"Final book types ({len(final_types)}):")
    for t in final_types:
        print(f"  - {t}")
    print()

if __name__ == '__main__':
    main()

