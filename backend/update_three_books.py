#!/usr/bin/env python3
"""Update three specific books with new cover URLs and published dates"""

import sqlite3
import os
from urllib.parse import urlparse

# Database path
DATABASE = 'films.db'

# Books to update: (book_name, cover_url, published_date)
BOOKS_TO_UPDATE = [
    ("The Right Stuff", "https://m.media-amazon.com/images/I/51W869WWQQL._AC_UF1000,1000_QL80_.jpg", "1979"),
    ("Animal Farm", "https://m.media-amazon.com/images/I/71je3-DsQEL._AC_UF1000,1000_QL80_.jpg", "1945"),
    ("Confessions of an Advertising Man", "https://m.media-amazon.com/images/S/compressed.photo.goodreads.com/books/1388252662i/44895.jpg", "1963"),
]

def update_books():
    """Update the three books with new cover URLs and published dates"""
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    
    for book_name, cover_url, published_date in BOOKS_TO_UPDATE:
        # Find the book by name (case-insensitive)
        cursor.execute('''
            SELECT id, book_name, cover_url, published_date 
            FROM books 
            WHERE LOWER(book_name) = LOWER(?)
        ''', (book_name,))
        
        book = cursor.fetchone()
        
        if book:
            book_id, current_name, current_cover, current_published = book
            print(f"\nFound: {current_name}")
            print(f"  Current cover: {current_cover}")
            print(f"  Current published_date: {current_published}")
            
            # Update the book
            cursor.execute('''
                UPDATE books 
                SET cover_url = ?, published_date = ?
                WHERE id = ?
            ''', (cover_url, published_date, book_id))
            
            print(f"  ✓ Updated cover URL")
            print(f"  ✓ Updated published_date to {published_date}")
        else:
            print(f"\n❌ Book not found: {book_name}")
            # Try to find similar names
            cursor.execute('''
                SELECT id, book_name 
                FROM books 
                WHERE book_name LIKE ?
            ''', (f'%{book_name}%',))
            similar = cursor.fetchall()
            if similar:
                print(f"  Similar books found:")
                for sid, sname in similar:
                    print(f"    - {sname} (ID: {sid})")
    
    conn.commit()
    conn.close()
    print("\n✓ Updates complete!")

if __name__ == '__main__':
    update_books()

