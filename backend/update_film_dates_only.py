#!/usr/bin/env python3
"""
Update only date_seen field for existing films from Google Sheets API
This prevents creating duplicates - only updates existing films
"""
import os
import sys
from google_sheets_service import get_films_data

def get_db():
    """Get database connection"""
    import sqlite3
    DATABASE = 'films.db'
    conn = sqlite3.connect(DATABASE, timeout=10.0)
    conn.row_factory = sqlite3.Row
    return conn

def main():
    print("=" * 80)
    print("UPDATING FILM DATES FROM GOOGLE SHEETS API")
    print("=" * 80)
    print()
    
    # Check credentials
    creds_path = os.getenv('GOOGLE_SHEETS_CREDENTIALS')
    creds_json = os.getenv('GOOGLE_SHEETS_CREDENTIALS_JSON')
    
    if not creds_path and not creds_json:
        print("❌ Error: Google Sheets credentials not configured")
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
    
    updated = 0
    not_found = 0
    
    def normalize_title(title):
        """Convert 'Title, The' to 'The Title' for matching"""
        if not title:
            return title
        if ',' in title:
            parts = [p.strip() for p in title.split(',')]
            if len(parts) == 2 and parts[1].lower() in ['the', 'a', 'an']:
                return f"{parts[1]} {parts[0]}"
        return title
    
    print("Updating existing films with dates...")
    for idx, row in enumerate(films_data, 1):
        order_number = row.get('Order', '')
        date_seen = row.get('Date Film Seen', row.get('Date Seen', '')).strip()
        title = row.get('Film', '').strip()
        release_year = row.get('Film Year', '')
        
        if not title:
            continue
        
        # Normalize title for matching (convert "Title, The" to "The Title")
        normalized_title = normalize_title(title)
        
        # Try to find existing film by order_number first
        film = None
        if order_number:
            try:
                cursor.execute("SELECT id FROM films WHERE order_number = ?", (int(order_number),))
                film = cursor.fetchone()
            except (ValueError, TypeError):
                pass
        
        # If not found, try by normalized title + release_year
        if not film and release_year and release_year != 'NA':
            try:
                release_year_int = int(release_year)
                # Try both original and normalized title
                cursor.execute("SELECT id FROM films WHERE (title = ? OR title = ?) AND release_year = ?", 
                              (title, normalized_title, release_year_int))
                film = cursor.fetchone()
            except (ValueError, TypeError):
                pass
        
        # If still not found, try just by title (both formats)
        if not film:
            cursor.execute("SELECT id FROM films WHERE title = ? OR title = ?", (title, normalized_title))
            film = cursor.fetchone()
        
        if film:
            film_id = film['id']
            cursor.execute("UPDATE films SET date_seen = ? WHERE id = ?", (date_seen, film_id))
            updated += 1
        else:
            not_found += 1
        
        if idx % 100 == 0:
            print(f"  Processed {idx} films... (updated: {updated}, not found: {not_found})")
            conn.commit()
    
    conn.commit()
    conn.close()
    
    print()
    print("=" * 80)
    print(f"✅ UPDATE COMPLETE")
    print("=" * 80)
    print(f"Updated: {updated} films with dates")
    print(f"Not found: {not_found} films")
    print()

if __name__ == '__main__':
    main()

