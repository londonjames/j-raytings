#!/usr/bin/env python3
"""
Import books from Google Sheets using the API (preserves exact dates)
This replaces the CSV import to get exact dates like "February 15, 1999"
"""
import os
import sys
from google_sheets_service import get_books_data
from google_books_service import search_book
from fix_author_names import fix_author_name
import time

# Import database functions from import_books.py
sys.path.insert(0, os.path.dirname(__file__))
from import_books import get_db, parse_int_or_none, parse_float_or_none, init_database

def main():
    print("=" * 80)
    print("IMPORTING BOOKS FROM GOOGLE SHEETS API")
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
    
    print("Initializing database...")
    init_database()
    
    print("Fetching books from Google Sheets API...")
    try:
        books_data = get_books_data()
        print(f"✓ Retrieved {len(books_data)} books from Google Sheets")
        print()
    except Exception as e:
        print(f"❌ Error fetching books: {e}")
        import traceback
        traceback.print_exc()
        return
    
    conn = get_db()
    cursor = conn.cursor()
    
    # Detect database type
    USE_POSTGRES = os.getenv('DATABASE_URL') is not None
    
    imported = 0
    updated = 0
    skipped = 0
    
    print("Processing books...")
    for idx, row in enumerate(books_data, 1):
        # Map columns (handle variations)
        order_number = parse_int_or_none(row.get('Order', ''))
        date_read = row.get('Date Read', '').strip()
        year = parse_int_or_none(row.get('Year', ''))
        book_name = row.get('Book Name', '').strip()
        author_raw = row.get('Author', '').strip()
        
        # Fix author name format: convert "Last, First" to "First Last"
        author = fix_author_name(author_raw) if author_raw else ''
        details_commentary = row.get('Details & Commentary', '').strip()
        j_rayting = row.get('J-Rayting', '').strip()
        score = parse_int_or_none(row.get('Score', ''))
        book_type = row.get('Type', '').strip()
        pages = parse_int_or_none(row.get('Pages', ''))
        form = row.get('Form', '').strip()
        notes_in_notion = row.get('Notes in Notion', '').strip()
        
        # Skip rows without order number or book name
        if order_number is None or not book_name:
            skipped += 1
            continue
        
        # Check if book already exists
        if USE_POSTGRES:
            cursor.execute("SELECT id FROM books WHERE order_number = %s", (order_number,))
        else:
            cursor.execute("SELECT id FROM books WHERE order_number = ?", (order_number,))
        
        existing = cursor.fetchone()
        
        if existing:
            # Update existing book
            book_id = existing[0] if USE_POSTGRES else existing['id']
            
            # Update date_read with exact date from API
            if USE_POSTGRES:
                cursor.execute("""
                    UPDATE books SET
                        date_read = %s,
                        year = %s,
                        book_name = %s,
                        author = %s,
                        details_commentary = %s,
                        j_rayting = %s,
                        score = %s,
                        type = %s,
                        pages = %s,
                        form = %s,
                        notes_in_notion = %s
                    WHERE id = %s
                """, (
                    date_read, year, book_name, author, details_commentary,
                    j_rayting, score, book_type, pages, form, notes_in_notion, book_id
                ))
            else:
                cursor.execute("""
                    UPDATE books SET
                        date_read = ?,
                        year = ?,
                        book_name = ?,
                        author = ?,
                        details_commentary = ?,
                        j_rayting = ?,
                        score = ?,
                        type = ?,
                        pages = ?,
                        form = ?,
                        notes_in_notion = ?
                    WHERE id = ?
                """, (
                    date_read, year, book_name, author, details_commentary,
                    j_rayting, score, book_type, pages, form, notes_in_notion, book_id
                ))
            
            updated += 1
        else:
            # Insert new book (without cover/API data for now - can be fetched separately)
            if USE_POSTGRES:
                cursor.execute("""
                    INSERT INTO books (
                        order_number, date_read, year, book_name, author,
                        details_commentary, j_rayting, score, type, pages,
                        form, notes_in_notion
                    )
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                """, (
                    order_number, date_read, year, book_name, author,
                    details_commentary, j_rayting, score, book_type, pages,
                    form, notes_in_notion
                ))
            else:
                cursor.execute("""
                    INSERT INTO books (
                        order_number, date_read, year, book_name, author,
                        details_commentary, j_rayting, score, type, pages,
                        form, notes_in_notion
                    )
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    order_number, date_read, year, book_name, author,
                    details_commentary, j_rayting, score, book_type, pages,
                    form, notes_in_notion
                ))
            
            imported += 1
        
        if (imported + updated) % 50 == 0:
            print(f"  Processed {imported + updated}/{len(books_data)} books...")
            conn.commit()
    
    conn.commit()
    conn.close()
    
    print()
    print("=" * 80)
    print("IMPORT COMPLETE!")
    print("=" * 80)
    print(f"Imported:   {imported} new books")
    print(f"Updated:    {updated} existing books")
    print(f"Skipped:    {skipped} rows")
    print()
    print("✅ Books imported with exact dates from Google Sheets API!")
    print("=" * 80)

if __name__ == '__main__':
    main()

