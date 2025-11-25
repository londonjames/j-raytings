#!/usr/bin/env python3
"""
Sync date_seen field from Google Sheets to production database

This script reads the "Date Film Seen" column from your Google Sheet
and updates the date_seen field in the production database.

Usage:
    # For production (requires DATABASE_URL env var):
    DATABASE_URL=your_postgres_url python3 sync_date_seen_from_sheet.py
    
    # For local SQLite:
    python3 sync_date_seen_from_sheet.py
"""

import csv
import urllib.request
import ssl
import sys
import os
from urllib.parse import urlparse

# Google Sheets CSV export URL
SHEET_URL = "https://docs.google.com/spreadsheets/d/1G4v10KupkEqA7gn6KZ1yZmXxc07-ymPPTDX4gxfudiA/export?format=csv&gid=0"
DATABASE = 'films.db'

# Detect if we should use PostgreSQL or SQLite
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

def get_db():
    """Get database connection (PostgreSQL or SQLite based on environment)"""
    if USE_POSTGRES:
        conn = psycopg2.connect(**DB_CONFIG)
        return conn
    else:
        conn = sqlite3.connect(DATABASE)
        conn.row_factory = sqlite3.Row
        return conn

def sync_date_seen():
    """Sync date_seen from Google Sheets to database"""
    print("=" * 60)
    print("Syncing date_seen from Google Sheets to database")
    print("=" * 60)
    
    if USE_POSTGRES:
        print("📊 Target: PostgreSQL (production)")
    else:
        print(f"📊 Target: SQLite ({DATABASE})")
    
    print("\n📥 Downloading CSV from Google Sheets...")
    
    try:
        # Download CSV (bypass SSL verification for development)
        context = ssl._create_unverified_context()
        response = urllib.request.urlopen(SHEET_URL, context=context)
        csv_data = response.read().decode('utf-8')
        
        # Parse CSV
        lines = csv_data.splitlines()
        
        # Skip the first empty line and remove leading empty column
        cleaned_lines = []
        for i, line in enumerate(lines):
            if i == 0:  # Skip first completely empty line
                continue
            # Remove leading comma (empty first column)
            if line.startswith(','):
                line = line[1:]
            cleaned_lines.append(line)
        
        csv_reader = csv.DictReader(cleaned_lines)
        
        # Build a mapping of order_number -> date_seen from the sheet
        sheet_data = {}
        for row in csv_reader:
            order_str = row.get('Order', '').strip()
            date_seen = row.get('Date Film Seen', '').strip()
            title = row.get('Film', '').strip()
            
            if not order_str or not order_str.isdigit():
                continue
            
            order_number = int(order_str)
            if date_seen:  # Only store non-empty dates
                sheet_data[order_number] = {
                    'date_seen': date_seen,
                    'title': title
                }
        
        print(f"✅ Loaded {len(sheet_data)} films with date_seen from Google Sheet")
        
        # Connect to database
        conn = get_db()
        if USE_POSTGRES:
            cursor = conn.cursor(cursor_factory=RealDictCursor)
        else:
            cursor = conn.cursor()
        
        # Get all films from database
        if USE_POSTGRES:
            cursor.execute('SELECT id, order_number, title, date_seen FROM films ORDER BY order_number')
        else:
            cursor.execute('SELECT id, order_number, title, date_seen FROM films ORDER BY order_number')
        
        db_films = cursor.fetchall()
        print(f"📊 Found {len(db_films)} films in database")
        
        # Update films
        updated_count = 0
        skipped_count = 0
        set_pre2006_count = 0
        
        print("\n🔄 Updating date_seen...")
        
        for film in db_films:
            film_id = film['id']
            order_number = film['order_number']
            db_title = film['title']
            # Handle both dict (PostgreSQL) and Row (SQLite) objects
            current_date_seen = film.get('date_seen') if hasattr(film, 'get') else (film['date_seen'] or '')
            
            if order_number in sheet_data:
                # Film has a date in the sheet
                sheet_date_seen = sheet_data[order_number]['date_seen']
                sheet_title = sheet_data[order_number]['title']
                
                # Skip if already matches
                if current_date_seen == sheet_date_seen:
                    skipped_count += 1
                    continue
                
                # Update the film with the date from sheet
                if USE_POSTGRES:
                    cursor.execute(
                        'UPDATE films SET date_seen = %s WHERE id = %s',
                        (sheet_date_seen, film_id)
                    )
                else:
                    cursor.execute(
                        'UPDATE films SET date_seen = ? WHERE id = ?',
                        (sheet_date_seen, film_id)
                    )
                
                updated_count += 1
            else:
                # Film not in sheet or has no date - set to "Pre-2006"
                if current_date_seen == 'Pre-2006':
                    skipped_count += 1
                    continue
                
                # Update to "Pre-2006"
                if USE_POSTGRES:
                    cursor.execute(
                        'UPDATE films SET date_seen = %s WHERE id = %s',
                        ('Pre-2006', film_id)
                    )
                else:
                    cursor.execute(
                        'UPDATE films SET date_seen = ? WHERE id = ?',
                        ('Pre-2006', film_id)
                    )
                
                set_pre2006_count += 1
            
            if (updated_count + set_pre2006_count) % 50 == 0:
                print(f"  Updated {updated_count + set_pre2006_count} films...")
        
        conn.commit()
        cursor.close()
        conn.close()
        
        print("\n" + "=" * 60)
        print("✅ Sync Complete!")
        print("=" * 60)
        print(f"📝 Updated with dates from sheet: {updated_count} films")
        print(f"📅 Set to 'Pre-2006' (no date in sheet): {set_pre2006_count} films")
        print(f"⏭️  Skipped (already matched): {skipped_count} films")
        print(f"📊 Total processed: {len(db_films)} films")
        
        # Show some examples of updated dates
        if updated_count > 0:
            print("\n📋 Sample updates:")
            conn = get_db()
            if USE_POSTGRES:
                cursor = conn.cursor(cursor_factory=RealDictCursor)
            else:
                cursor = conn.cursor()
            
            if USE_POSTGRES:
                cursor.execute('''
                    SELECT title, date_seen 
                    FROM films 
                    WHERE date_seen IS NOT NULL AND date_seen != ''
                    ORDER BY order_number 
                    LIMIT 10
                ''')
            else:
                cursor.execute('''
                    SELECT title, date_seen 
                    FROM films 
                    WHERE date_seen IS NOT NULL AND date_seen != ''
                    ORDER BY order_number 
                    LIMIT 10
                ''')
            
            samples = cursor.fetchall()
            for sample in samples:
                print(f"  • {sample['title']}: {sample['date_seen']}")
            
            cursor.close()
            conn.close()
        
    except Exception as e:
        print(f"\n❌ Error syncing date_seen: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == '__main__':
    sync_date_seen()

