#!/usr/bin/env python3
"""
Update book dates from Google Sheets to preserve exact dates like "February 15, 1999"
This script reads the Google Sheets CSV and updates the date_read field with exact dates
"""
import csv
import sqlite3
import urllib.request
import ssl
import os

# Google Sheets CSV export URL (gid=2 for the books tab)
SHEET_URL = "https://docs.google.com/spreadsheets/d/1G4v10KupkEqA7gn6KZ1yZmXxc07-ymPPTDX4gxfudiA/export?format=csv&gid=2"
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

def main():
    print("=" * 80)
    print("UPDATING BOOK DATES FROM GOOGLE SHEETS")
    print("=" * 80)
    print()

    print("Downloading CSV from Google Sheets...")
    try:
        context = ssl._create_unverified_context()
        response = urllib.request.urlopen(SHEET_URL, context=context)
        csv_data = response.read().decode('utf-8')
        
        lines = csv_data.splitlines()
        cleaned_lines = []
        for i, line in enumerate(lines):
            if i == 0:
                continue
            if line.startswith(','):
                line = line[1:]
            cleaned_lines.append(line)
        
        csv_reader = csv.DictReader(cleaned_lines)
        
        conn = get_db()
        cursor = conn.cursor()
        
        updated = 0
        not_found = 0
        
        print("Updating dates...")
        for row in csv_reader:
            book_name = row.get('Book Name', '').strip()
            date_read = row.get('Date Read', '').strip()
            
            if not book_name or not date_read:
                continue
            
            # Try to find the book by name (handle "Title, The" vs "The Title")
            # First try exact match
            if USE_POSTGRES:
                cursor.execute("SELECT id FROM books WHERE book_name = %s", (book_name,))
            else:
                cursor.execute("SELECT id FROM books WHERE book_name = ?", (book_name,))
            
            book = cursor.fetchone()
            
            if not book:
                # Try reversed format (e.g., "Right Stuff, The" -> "The Right Stuff")
                if ', The' in book_name:
                    reversed_name = f"The {book_name.replace(', The', '')}"
                    if USE_POSTGRES:
                        cursor.execute("SELECT id FROM books WHERE book_name = %s", (reversed_name,))
                    else:
                        cursor.execute("SELECT id FROM books WHERE book_name = ?", (reversed_name,))
                    book = cursor.fetchone()
                    if book:
                        book_name = reversed_name
            
            if book:
                book_id = book[0] if USE_POSTGRES else book['id']
                if USE_POSTGRES:
                    cursor.execute("UPDATE books SET date_read = %s WHERE id = %s", (date_read, book_id))
                else:
                    cursor.execute("UPDATE books SET date_read = ? WHERE id = ?", (date_read, book_id))
                updated += 1
                if updated % 50 == 0:
                    print(f"  Updated {updated} books...")
            else:
                not_found += 1
                if not_found <= 10:  # Only show first 10 not found
                    print(f"  ⚠️  Not found: {book_name}")
        
        conn.commit()
        conn.close()
        
        print()
        print("=" * 80)
        print("UPDATE COMPLETE!")
        print("=" * 80)
        print(f"Updated:    {updated} books")
        if not_found > 0:
            print(f"Not found:  {not_found} books")
        print("=" * 80)
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    main()

