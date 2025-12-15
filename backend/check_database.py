#!/usr/bin/env python3
"""Check which database is being accessed"""
import os
import sqlite3
from urllib.parse import urlparse

DATABASE_URL = os.getenv('DATABASE_URL')
USE_POSTGRES = DATABASE_URL is not None

print("=" * 60)
print("DATABASE CONNECTION CHECK")
print("=" * 60)

if USE_POSTGRES:
    print("✓ Using PostgreSQL")
    result = urlparse(DATABASE_URL)
    db_name = result.path[1:] if result.path else None
    
    print(f"\nDatabase URL: {DATABASE_URL[:50]}..." if len(DATABASE_URL) > 50 else f"\nDatabase URL: {DATABASE_URL}")
    print(f"Database Name: {db_name}")
    print(f"Host: {result.hostname}")
    print(f"Port: {result.port}")
    print(f"User: {result.username}")
    
    # Try to connect and verify
    try:
        import psycopg2
        conn = psycopg2.connect(
            dbname=db_name,
            user=result.username,
            password=result.password,
            host=result.hostname,
            port=result.port
        )
        cursor = conn.cursor()
        cursor.execute("SELECT current_database();")
        actual_db_name = cursor.fetchone()[0]
        print(f"\n✓ Successfully connected!")
        print(f"  Current database: {actual_db_name}")
        
        # Check if it matches "j-raytings"
        if actual_db_name == "j-raytings" or actual_db_name == "j_raytings":
            print(f"  ✓ Confirmed: Accessing 'j-raytings' database")
        elif "rayting" in actual_db_name.lower():
            print(f"  ✓ Database name contains 'rayting': '{actual_db_name}'")
        else:
            print(f"  ⚠️  Database name is '{actual_db_name}'")
            print(f"     Expected: 'j-raytings' or 'j_raytings'")
        
        # Get table count
        cursor.execute("""
            SELECT COUNT(*) 
            FROM information_schema.tables 
            WHERE table_schema = 'public'
        """)
        table_count = cursor.fetchone()[0]
        print(f"  Tables in database: {table_count}")
        
        # Check for films and books tables
        cursor.execute("""
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_schema = 'public' 
            AND table_name IN ('films', 'books')
        """)
        tables = [row[0] for row in cursor.fetchall()]
        print(f"  Found tables: {', '.join(tables) if tables else 'None'}")
        
        conn.close()
    except Exception as e:
        print(f"\n✗ Connection failed: {e}")
else:
    print("✓ Using SQLite")
    DATABASE = 'films.db'
    print(f"\nDatabase file: {DATABASE}")
    
    if os.path.exists(DATABASE):
        print(f"✓ Database file exists")
        try:
            conn = sqlite3.connect(DATABASE)
            cursor = conn.cursor()
            
            # Get all tables
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
            tables = [row[0] for row in cursor.fetchall()]
            print(f"  Tables: {', '.join(tables) if tables else 'None'}")
            
            # Count films
            if 'films' in tables:
                cursor.execute("SELECT COUNT(*) FROM films")
                film_count = cursor.fetchone()[0]
                print(f"  Films: {film_count}")
            
            # Count books
            if 'books' in tables:
                cursor.execute("SELECT COUNT(*) FROM books")
                book_count = cursor.fetchone()[0]
                print(f"  Books: {book_count}")
            
            conn.close()
            print(f"\n✓ SQLite database accessible")
        except Exception as e:
            print(f"\n✗ Error accessing SQLite database: {e}")
    else:
        print(f"✗ Database file does not exist")

print("\n" + "=" * 60)
