#!/usr/bin/env python3
"""
Add date_seen column to production database if it doesn't exist
"""

import os
from urllib.parse import urlparse

DATABASE_URL = os.getenv('DATABASE_URL')

if not DATABASE_URL:
    print("❌ DATABASE_URL environment variable not set")
    print("This script is for production database only")
    exit(1)

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

def check_column_exists(cursor, column_name):
    """Check if a column exists in the films table"""
    cursor.execute("""
        SELECT column_name 
        FROM information_schema.columns 
        WHERE table_name='films' AND column_name=%s
    """, (column_name,))
    return cursor.fetchone() is not None

def add_date_seen_column():
    """Add date_seen column if it doesn't exist"""
    conn = psycopg2.connect(**DB_CONFIG)
    cursor = conn.cursor()
    
    try:
        # Check if column exists
        if check_column_exists(cursor, 'date_seen'):
            print("✅ Column 'date_seen' already exists")
        else:
            print("Adding 'date_seen' column...")
            cursor.execute('ALTER TABLE films ADD COLUMN date_seen TEXT')
            conn.commit()
            print("✅ Successfully added 'date_seen' column")
        
        # Verify
        cursor.execute("SELECT COUNT(*) FROM films WHERE date_seen IS NOT NULL AND date_seen != ''")
        count = cursor.fetchone()[0]
        print(f"📊 Films with date_seen data: {count}")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        conn.rollback()
    finally:
        cursor.close()
        conn.close()

if __name__ == '__main__':
    add_date_seen_column()

