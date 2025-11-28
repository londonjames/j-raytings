#!/usr/bin/env python3
"""Migrate published_date to year_written for the three books"""

import sqlite3

DATABASE = 'films.db'

# Books to migrate
BOOKS_TO_MIGRATE = [
    "The Right Stuff",
    "Animal Farm",
    "Confessions of an Advertising Man"
]

def migrate_books():
    """Copy published_date to year_written for the three books"""
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    
    for book_name in BOOKS_TO_MIGRATE:
        # Get the book's published_date
        cursor.execute('''
            SELECT id, book_name, published_date, year_written 
            FROM books 
            WHERE LOWER(book_name) = LOWER(?)
        ''', (book_name,))
        
        book = cursor.fetchone()
        
        if book:
            book_id, name, published_date, year_written = book
            print(f"\n{name}:")
            print(f"  Current published_date: {published_date}")
            print(f"  Current year_written: {year_written}")
            
            # Extract year from published_date if it exists
            if published_date and not year_written:
                # Try to extract year (format: "1979" or "1979-03-04")
                year_match = None
                if isinstance(published_date, str):
                    year_match = published_date[:4] if len(published_date) >= 4 else None
                elif isinstance(published_date, int):
                    year_match = str(published_date)
                
                if year_match and year_match.isdigit():
                    year_int = int(year_match)
                    cursor.execute('''
                        UPDATE books 
                        SET year_written = ?
                        WHERE id = ?
                    ''', (year_int, book_id))
                    print(f"  ✓ Set year_written to {year_int}")
                else:
                    print(f"  ⚠ Could not extract year from: {published_date}")
            elif year_written:
                print(f"  ✓ Already has year_written: {year_written}")
            else:
                print(f"  ⚠ No published_date to migrate")
    
    conn.commit()
    conn.close()
    print("\n✓ Migration complete!")

if __name__ == '__main__':
    migrate_books()

