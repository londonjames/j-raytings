#!/usr/bin/env python3
"""
Update Notion links in the database from Google Sheets
Extracts hyperlinks from the "Notes in Notion" column and updates the database
"""
import os
import sys
from google_sheets_service import get_books_data
from import_books import get_db, init_database

def main():
    print("=" * 80)
    print("UPDATING NOTION LINKS FROM GOOGLE SHEETS")
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
        return
    
    print("Initializing database...")
    init_database()
    
    print("Fetching books from Google Sheets API (with Notion links)...")
    try:
        books_data = get_books_data()
        print(f"✓ Retrieved {len(books_data)} books from Google Sheets")
        print()
    except Exception as e:
        print(f"❌ Error fetching books: {e}")
        import traceback
        traceback.print_exc()
        return
    
    # Count books with Notion links
    books_with_links = [b for b in books_data if b.get('Notion Link')]
    print(f"✓ Found {len(books_with_links)} books with Notion links in Google Sheets")
    print()
    
    # Update database
    db = get_db()
    updated_count = 0
    new_count = 0
    skipped_count = 0
    
    print("Updating Notion links in database...")
    print()
    
    for book in books_data:
        order_number = book.get('Order', '').strip()
        if not order_number:
            continue
        
        notion_link = book.get('Notion Link', '').strip()
        notes_in_notion = book.get('Notes in Notion', '').strip()
        
        # Only update if there's a Notion link
        if not notion_link:
            if notes_in_notion == 'YES':
                skipped_count += 1
            continue
        
        try:
            order_num = int(order_number)
        except ValueError:
            continue
        
        # Check if book exists
        cursor = db.cursor()
        cursor.execute('SELECT id, notion_link FROM books WHERE order_number = ?', (order_num,))
        existing = cursor.fetchone()
        
        if existing:
            book_id, existing_link = existing
            if existing_link != notion_link:
                # Update existing book
                cursor.execute(
                    'UPDATE books SET notion_link = ? WHERE id = ?',
                    (notion_link, book_id)
                )
                updated_count += 1
                print(f"  ✓ Updated order {order_num}: {notion_link[:60]}...")
            else:
                skipped_count += 1
        else:
            # Book doesn't exist, skip (we only update existing books)
            skipped_count += 1
    
    db.commit()
    db.close()
    
    print()
    print("=" * 80)
    print("SUMMARY")
    print("=" * 80)
    print(f"  Books with Notion links in Google Sheets: {len(books_with_links)}")
    print(f"  Updated in database: {updated_count}")
    print(f"  Already up to date: {skipped_count}")
    print(f"  New links added: {new_count}")
    print()
    print("✓ Notion links update complete!")

if __name__ == '__main__':
    main()
