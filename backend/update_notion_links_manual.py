#!/usr/bin/env python3
"""
Manually update Notion links and notes_in_notion status from user-provided list
"""
import os
import sys
from import_books import get_db, init_database

def normalize_title(title):
    """Normalize title for matching (handle 'The' variations)"""
    title = title.strip()
    # Handle "Title, The" -> "The Title"
    if title.endswith(', The'):
        title = f"The {title[:-5]}"
    return title.strip()

def update_books_from_list(updates):
    """
    Update books based on provided list
    
    Args:
        updates: List of tuples (book_title, action)
                action can be "CHANGE TO NO" or a URL string
    """
    print("=" * 80)
    print("MANUAL NOTION LINKS UPDATE")
    print("=" * 80)
    print()
    
    init_database()
    db = get_db()
    
    updated_links = 0
    changed_to_no = 0
    not_found = []
    
    print(f"Processing {len(updates)} updates...\n")
    
    for book_title, action in updates:
        normalized_title = normalize_title(book_title)
        
        cursor = db.cursor()
        
        # Try exact match first
        cursor.execute(
            'SELECT id, book_name, notion_link, notes_in_notion FROM books WHERE book_name = ?',
            (book_title,)
        )
        book = cursor.fetchone()
        
        # If not found, try normalized version
        if not book:
            cursor.execute(
                'SELECT id, book_name, notion_link, notes_in_notion FROM books WHERE book_name = ?',
                (normalized_title,)
            )
            book = cursor.fetchone()
        
        # If still not found, try case-insensitive match
        if not book:
            cursor.execute(
                'SELECT id, book_name, notion_link, notes_in_notion FROM books WHERE LOWER(book_name) = LOWER(?)',
                (book_title,)
            )
            book = cursor.fetchone()
        
        if not book:
            not_found.append(book_title)
            print(f"  ⚠️  NOT FOUND: {book_title}")
            continue
        
        book_id, db_title, existing_link, existing_notes = book
        
        if action == "CHANGE TO NO":
            # Update notes_in_notion to NO
            cursor.execute(
                'UPDATE books SET notes_in_notion = ? WHERE id = ?',
                ('NO', book_id)
            )
            changed_to_no += 1
            print(f"  ✓ Changed to NO: {db_title}")
        else:
            # Update with hyperlink
            url = action.strip()
            if existing_link != url:
                cursor.execute(
                    'UPDATE books SET notion_link = ?, notes_in_notion = ? WHERE id = ?',
                    (url, 'YES', book_id)
                )
                updated_links += 1
                print(f"  ✓ Updated link: {db_title}")
                print(f"    {url[:60]}...")
            else:
                print(f"  - Already up to date: {db_title}")
    
    db.commit()
    db.close()
    
    print()
    print("=" * 80)
    print("SUMMARY")
    print("=" * 80)
    print(f"  Links updated: {updated_links}")
    print(f"  Changed to NO: {changed_to_no}")
    print(f"  Not found: {len(not_found)}")
    if not_found:
        print(f"\n  Books not found:")
        for title in not_found:
            print(f"    - {title}")
    print()
    print("✓ Update complete!\n")

if __name__ == '__main__':
    # Parse input from command line or stdin
    updates = []
    
    if len(sys.argv) > 1:
        # Read from file
        with open(sys.argv[1], 'r') as f:
            for line in f:
                line = line.strip()
                if not line or line.startswith('#'):
                    continue
                if ';' in line:
                    parts = line.split(';', 1)
                    title = parts[0].strip()
                    action = parts[1].strip()
                    updates.append((title, action))
    else:
        # Read from stdin
        print("Enter book updates (format: Book Title; URL or CHANGE TO NO)")
        print("Press Ctrl+D (Unix) or Ctrl+Z (Windows) when done")
        print()
        for line in sys.stdin:
            line = line.strip()
            if not line:
                continue
            if ';' in line:
                parts = line.split(';', 1)
                title = parts[0].strip()
                action = parts[1].strip()
                updates.append((title, action))
    
    if updates:
        update_books_from_list(updates)
    else:
        print("No updates provided")
