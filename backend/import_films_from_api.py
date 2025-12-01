#!/usr/bin/env python3
"""
Import films from Google Sheets using the API (preserves exact dates)
This replaces the CSV import to get exact dates like "February 15, 1999"
"""
import os
import sys
from google_sheets_service import get_films_data
import time

# Import database functions from import_films.py
sys.path.insert(0, os.path.dirname(__file__))
from import_films import parse_int_or_none, parse_year_watched

def get_db():
    """Get database connection"""
    import sqlite3
    DATABASE = 'films.db'
    conn = sqlite3.connect(DATABASE, timeout=10.0)
    conn.row_factory = sqlite3.Row
    return conn

def main():
    print("=" * 80)
    print("IMPORTING FILMS FROM GOOGLE SHEETS API")
    print("=" * 80)
    print()
    
    # Check credentials
    creds_path = os.getenv('GOOGLE_SHEETS_CREDENTIALS')
    creds_json = os.getenv('GOOGLE_SHEETS_CREDENTIALS_JSON')
    
    if not creds_path and not creds_json:
        print("❌ Error: Google Sheets credentials not configured")
        print()
        print("Please set one of:")
        print("  - GOOGLE_SHEETS_CREDENTIALS (path to JSON file)")
        print("  - GOOGLE_SHEETS_CREDENTIALS_JSON (JSON string)")
        print()
        print("See GOOGLE_SHEETS_SETUP.md for instructions")
        return
    
    print("Fetching films from Google Sheets API...")
    try:
        films_data = get_films_data()
        print(f"✓ Retrieved {len(films_data)} films from Google Sheets")
        print()
    except Exception as e:
        print(f"❌ Error fetching films: {e}")
        import traceback
        traceback.print_exc()
        return
    
    conn = get_db()
    cursor = conn.cursor()
    
    imported = 0
    updated = 0
    skipped = 0
    
    print("Processing films...")
    for idx, row in enumerate(films_data, 1):
        # Map columns (handle variations)
        order_number = parse_int_or_none(row.get('Order', ''))
        date_seen = row.get('Date Film Seen', row.get('Date Seen', '')).strip()
        title = row.get('Film', '').strip()
        letter_rating = row.get('J-Rayting', '').strip()
        score = parse_int_or_none(row.get('Score', ''))
        year_watched = parse_year_watched(row.get('Year', '').strip())
        location = row.get('Location Seen', '').strip()
        format_type = row.get('Film Format', '').strip()
        release_year = parse_int_or_none(row.get('Film Year', ''))
        rotten_tomatoes = row.get('Rotten Tomatoes', '').strip()
        length_minutes = parse_int_or_none(row.get('Film Length', ''))
        rt_per_minute = row.get('RT% per minute', '').strip()
        
        # Skip rows without order number or title
        if order_number is None or not title:
            skipped += 1
            continue
        
        # Check if film already exists (by title and release_year for better matching)
        cursor.execute("SELECT id FROM films WHERE title = ? AND release_year = ?", (title, release_year))
        existing = cursor.fetchone()
        
        if not existing and order_number:
            # Fallback: try matching by order_number
            cursor.execute("SELECT id FROM films WHERE order_number = ?", (order_number,))
            existing = cursor.fetchone()
        
        if existing:
            # Update existing film
            film_id = existing['id'] if isinstance(existing, dict) else existing[0]
            
            # Update date_seen with exact date from API
            cursor.execute("""
                UPDATE films SET
                    date_seen = ?,
                    title = ?,
                    letter_rating = ?,
                    score = ?,
                    year_watched = ?,
                    location = ?,
                    format = ?,
                    release_year = ?,
                    rotten_tomatoes = ?,
                    length_minutes = ?,
                    rt_per_minute = ?
                WHERE id = ?
            """, (
                date_seen if date_seen else None,
                title,
                letter_rating if letter_rating else None,
                score,
                year_watched,
                location if location else None,
                format_type if format_type else None,
                release_year,
                rotten_tomatoes if rotten_tomatoes else None,
                length_minutes,
                rt_per_minute if rt_per_minute else None,
                film_id
            ))
            updated += 1
        else:
            # Insert new film
            cursor.execute("""
                INSERT INTO films (
                    order_number, date_seen, title, letter_rating, score,
                    year_watched, location, format, release_year,
                    rotten_tomatoes, length_minutes, rt_per_minute
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                order_number,
                date_seen if date_seen else None,
                title,
                letter_rating if letter_rating else None,
                score,
                year_watched,
                location if location else None,
                format_type if format_type else None,
                release_year,
                rotten_tomatoes if rotten_tomatoes else None,
                length_minutes,
                rt_per_minute if rt_per_minute else None
            ))
            imported += 1
        
        if idx % 100 == 0:
            print(f"  Processed {idx} films... (imported: {imported}, updated: {updated}, skipped: {skipped})")
            conn.commit()
    
    conn.commit()
    conn.close()
    
    print()
    print("=" * 80)
    print(f"✅ IMPORT COMPLETE")
    print("=" * 80)
    print(f"Imported: {imported} new films")
    print(f"Updated: {updated} existing films")
    print(f"Skipped: {skipped} rows")
    print()

if __name__ == '__main__':
    main()

