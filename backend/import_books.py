import csv
import sqlite3
import urllib.request
import ssl
import sys
import os
import time
from google_books_service import search_book

# Google Sheets CSV export URL (gid=2 for the books tab)
SHEET_URL = "https://docs.google.com/spreadsheets/d/1G4v10KupkEqA7gn6KZ1yZmXxc07-ymPPTDX4gxfudiA/export?format=csv&gid=2"
DATABASE = 'films.db'  # Using same database file

# Detect if we should use PostgreSQL or SQLite
DATABASE_URL = os.getenv('DATABASE_URL')
USE_POSTGRES = DATABASE_URL is not None

if USE_POSTGRES:
    import psycopg2
    from urllib.parse import urlparse
    
    # Parse DATABASE_URL for psycopg2
    result = urlparse(DATABASE_URL)
    DB_CONFIG = {
        'dbname': result.path[1:],
        'user': result.username,
        'password': result.password,
        'host': result.hostname,
        'port': result.port
    }

def get_db():
    """Get database connection (PostgreSQL or SQLite based on environment)"""
    if USE_POSTGRES:
        conn = psycopg2.connect(**DB_CONFIG)
        return conn
    else:
        # Use timeout to wait for lock to be released
        conn = sqlite3.connect(DATABASE, timeout=30.0)
        conn.row_factory = sqlite3.Row
        return conn

def parse_int_or_none(value):
    """Parse integer or return None"""
    if value is None:
        return None
    if isinstance(value, (int, float)):
        return int(value)
    if isinstance(value, str):
        if not value or value.strip() == '':
            return None
        try:
            return int(value)
        except ValueError:
            return None
    return None

def parse_float_or_none(value):
    """Parse float or return None"""
    if value is None:
        return None
    if isinstance(value, (int, float)):
        return float(value)
    if isinstance(value, str):
        if not value or value.strip() == '':
            return None
        try:
            return float(value)
        except ValueError:
            return None
    return None

def init_database():
    """Initialize the database with the books table"""
    from app import init_books_db
    init_books_db()

def import_books():
    """Import books from Google Sheets CSV"""
    print("Initializing database...")
    init_database()

    print("Downloading CSV from Google Sheets...")

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

        # Connect to database
        conn = get_db()
        cursor = conn.cursor()

        # Clear existing data (optional - comment out if you want to keep existing books)
        print("Clearing existing books...")
        try:
            cursor.execute('DELETE FROM books')
            conn.commit()
        except Exception as e:
            print(f"Warning: Could not clear existing books (database may be locked): {e}")
            print("Continuing with import...")

        count = 0
        skipped = 0
        print("Importing books...")

        for row in csv_reader:
            # Map CSV columns to database fields
            order_number = parse_int_or_none(row.get('Order', ''))
            date_read = row.get('Date Read', '').strip()
            year = parse_int_or_none(row.get('Year', ''))
            book_name = row.get('Book Name', '').strip()
            author = row.get('Author', '').strip()
            details_commentary = row.get('Details & Commentary', '').strip()
            j_rayting = row.get('J-Rayting', '').strip()
            score = parse_int_or_none(row.get('Score', ''))
            book_type = row.get('Type', '').strip()
            pages = parse_int_or_none(row.get('Pages', ''))
            form = row.get('Form', '').strip()
            notes_in_notion = row.get('Notes in Notion', '').strip()

            # Skip rows without an Order number (stats, summaries, etc.)
            if order_number is None:
                continue

            # Skip rows without a book name
            if not book_name:
                continue

            # Search Google Books API for metadata
            print(f"  [{count+1}] Fetching data for '{book_name}' by {author or 'Unknown'}...")
            book_data = search_book(book_name, author)
            
            # Extract data from Google Books API response
            cover_url = None
            google_books_id = None
            isbn = None
            average_rating = None
            ratings_count = None
            published_date = None
            description = None
            
            if book_data:
                cover_url = book_data.get('cover_url')
                google_books_id = book_data.get('google_books_id')
                isbn = book_data.get('isbn')
                average_rating = parse_float_or_none(book_data.get('average_rating'))
                ratings_count = parse_int_or_none(book_data.get('ratings_count'))
                published_date = book_data.get('published_date')
                description = book_data.get('description')
            else:
                skipped += 1
                print(f"      ⚠️  No data found in Google Books API")

            # Insert into database
            if USE_POSTGRES:
                cursor.execute('''
                    INSERT INTO books (
                        order_number, date_read, year, book_name, author,
                        details_commentary, j_rayting, score, type, pages,
                        form, notes_in_notion, cover_url, google_books_id,
                        isbn, average_rating, ratings_count, published_date, description
                    )
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                ''', (
                    order_number, date_read, year, book_name, author,
                    details_commentary, j_rayting, score, book_type, pages,
                    form, notes_in_notion, cover_url, google_books_id,
                    isbn, average_rating, ratings_count, published_date, description
                ))
            else:
                cursor.execute('''
                    INSERT INTO books (
                        order_number, date_read, year, book_name, author,
                        details_commentary, j_rayting, score, type, pages,
                        form, notes_in_notion, cover_url, google_books_id,
                        isbn, average_rating, ratings_count, published_date, description
                    )
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    order_number, date_read, year, book_name, author,
                    details_commentary, j_rayting, score, book_type, pages,
                    form, notes_in_notion, cover_url, google_books_id,
                    isbn, average_rating, ratings_count, published_date, description
                ))

            count += 1
            
            # Commit after each book to avoid long transactions
            conn.commit()
            
            # Rate limiting - Google Books allows 1000 requests/day free tier
            # Add small delay to avoid hitting rate limits
            if count % 10 == 0:
                print(f"  Imported {count} books...")
                time.sleep(0.5)  # Small delay every 10 books
            else:
                time.sleep(0.25)  # Small delay between requests

        conn.commit()
        conn.close()

        print(f"\n✅ Successfully imported {count} books!")
        if skipped > 0:
            print(f"⚠️  {skipped} books had no Google Books data")
        print(f"Database: {DATABASE if not USE_POSTGRES else 'PostgreSQL'}")

    except Exception as e:
        print(f"\n❌ Error importing books: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == '__main__':
    import_books()

