#!/usr/bin/env python3
"""
Update all VHS and DVD format entries to be capitalized in the database
"""

import os
import sys
from urllib.parse import urlparse

# Check if we're using PostgreSQL (production) or SQLite (local)
DATABASE_URL = os.getenv('DATABASE_URL')
USE_POSTGRES = DATABASE_URL is not None

if USE_POSTGRES:
    import psycopg2
    from psycopg2.extras import RealDictCursor
    
    # Parse DATABASE_URL for psycopg2
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
    DATABASE = 'films.db'

def get_db():
    """Get database connection (PostgreSQL or SQLite based on environment)"""
    if USE_POSTGRES:
        conn = psycopg2.connect(**DB_CONFIG)
        return conn
    else:
        conn = sqlite3.connect(DATABASE)
        conn.row_factory = sqlite3.Row
        return conn

def capitalize_vhs_dvd():
    """Capitalize all VHS and DVD format entries"""
    conn = get_db()
    cursor = conn.cursor()
    
    print("Capitalizing VHS and DVD formats...")
    
    if USE_POSTGRES:
        # PostgreSQL: Update VHS (case-insensitive)
        cursor.execute("""
            UPDATE films 
            SET format = 'VHS' 
            WHERE LOWER(format) = 'vhs'
        """)
        vhs_count = cursor.rowcount
        print(f"✓ Updated {vhs_count} VHS entries")
        
        # PostgreSQL: Update DVD (case-insensitive)
        cursor.execute("""
            UPDATE films 
            SET format = 'DVD' 
            WHERE LOWER(format) = 'dvd'
        """)
        dvd_count = cursor.rowcount
        print(f"✓ Updated {dvd_count} DVD entries")
    else:
        # SQLite: Update VHS (case-insensitive)
        cursor.execute("""
            UPDATE films 
            SET format = 'VHS' 
            WHERE LOWER(format) = 'vhs'
        """)
        vhs_count = cursor.rowcount
        print(f"✓ Updated {vhs_count} VHS entries")
        
        # SQLite: Update DVD (case-insensitive)
        cursor.execute("""
            UPDATE films 
            SET format = 'DVD' 
            WHERE LOWER(format) = 'dvd'
        """)
        dvd_count = cursor.rowcount
        print(f"✓ Updated {dvd_count} DVD entries")
    
    conn.commit()
    
    # Show final counts
    if USE_POSTGRES:
        cursor.execute("""
            SELECT format, COUNT(*) as count 
            FROM films 
            WHERE format IN ('VHS', 'DVD') 
            GROUP BY format 
            ORDER BY format
        """)
    else:
        cursor.execute("""
            SELECT format, COUNT(*) as count 
            FROM films 
            WHERE format IN ('VHS', 'DVD') 
            GROUP BY format 
            ORDER BY format
        """)
    
    results = cursor.fetchall()
    
    print("\n📊 Final VHS/DVD counts:")
    for format_name, count in results:
        print(f"  {format_name}: {count}")
    
    conn.close()
    print("\n✅ Format capitalization complete!")

if __name__ == '__main__':
    capitalize_vhs_dvd()

