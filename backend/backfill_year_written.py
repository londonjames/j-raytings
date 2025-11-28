#!/usr/bin/env python3
"""Backfill year_written from published_date for all books"""

import sqlite3
import os

DATABASE = 'films.db'

def backfill_year_written():
    """Extract year from published_date and set year_written"""
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    
    # Get all books with published_date but no year_written
    cursor.execute('''
        SELECT id, book_name, published_date, year_written 
        FROM books 
        WHERE published_date IS NOT NULL 
        AND published_date != ''
        AND (year_written IS NULL OR year_written = 0)
    ''')
    
    books = cursor.fetchall()
    print(f"Found {len(books)} books with published_date but no year_written\n")
    
    updated_count = 0
    for book_id, book_name, published_date, year_written in books:
        # Extract year from published_date (format: "1979", "1979-03-04", "2008-03-04", etc.)
        year = None
        
        if isinstance(published_date, str):
            # Try to extract 4-digit year from the beginning
            year_match = published_date[:4] if len(published_date) >= 4 else None
            if year_match and year_match.isdigit():
                year = int(year_match)
        elif isinstance(published_date, int):
            # If it's already an integer, use it directly (but check it's reasonable)
            if 0 < published_date < 3000:
                year = published_date
        
        if year:
            cursor.execute('''
                UPDATE books 
                SET year_written = ?
                WHERE id = ?
            ''', (year, book_id))
            updated_count += 1
            print(f"✓ {book_name}: {published_date} → year_written = {year}")
        else:
            print(f"⚠ {book_name}: Could not extract year from '{published_date}'")
    
    conn.commit()
    
    # Also update books that have year_written = 0 but have published_date
    cursor.execute('''
        SELECT id, book_name, published_date, year_written 
        FROM books 
        WHERE published_date IS NOT NULL 
        AND published_date != ''
        AND year_written = 0
    ''')
    
    books_zero = cursor.fetchall()
    if books_zero:
        print(f"\nFound {len(books_zero)} books with year_written = 0, updating...")
        for book_id, book_name, published_date, year_written in books_zero:
            year = None
            if isinstance(published_date, str):
                year_match = published_date[:4] if len(published_date) >= 4 else None
                if year_match and year_match.isdigit():
                    year = int(year_match)
            elif isinstance(published_date, int):
                if 0 < published_date < 3000:
                    year = published_date
            
            if year:
                cursor.execute('''
                    UPDATE books 
                    SET year_written = ?
                    WHERE id = ?
                ''', (year, book_id))
                updated_count += 1
                print(f"✓ {book_name}: {published_date} → year_written = {year}")
    
    conn.commit()
    conn.close()
    
    print(f"\n✓ Backfill complete! Updated {updated_count} books.")

if __name__ == '__main__':
    backfill_year_written()

