#!/usr/bin/env python3
"""
Test Google Sheets API integration
"""
import os
from google_sheets_service import get_books_data, get_films_data

def main():
    print("=" * 80)
    print("TESTING GOOGLE SHEETS API")
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
    
    print("✓ Credentials found")
    print()
    
    # Test reading books
    print("📚 Testing books data retrieval...")
    try:
        books = get_books_data()
        print(f"✓ Retrieved {len(books)} books")
        
        if books:
            # Show first book with date
            first_book = books[0]
            print(f"\nFirst book:")
            print(f"  Name: {first_book.get('Book Name', 'N/A')}")
            print(f"  Date Read: {first_book.get('Date Read', 'N/A')}")
            print(f"  Author: {first_book.get('Author', 'N/A')}")
    except Exception as e:
        print(f"❌ Error reading books: {e}")
        import traceback
        traceback.print_exc()
        return
    
    print()
    
    # Test reading films
    print("🎬 Testing films data retrieval...")
    try:
        films = get_films_data()
        print(f"✓ Retrieved {len(films)} films")
        
        if films:
            # Show first film with date
            first_film = films[0]
            print(f"\nFirst film:")
            print(f"  Title: {first_film.get('Film', first_film.get('Title', 'N/A'))}")
            print(f"  Date Seen: {first_film.get('Date Film Seen', first_film.get('Date Seen', 'N/A'))}")
    except Exception as e:
        print(f"❌ Error reading films: {e}")
        import traceback
        traceback.print_exc()
        return
    
    print()
    print("=" * 80)
    print("✅ ALL TESTS PASSED!")
    print("=" * 80)

if __name__ == '__main__':
    main()

