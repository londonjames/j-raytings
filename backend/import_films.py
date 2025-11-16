import csv
import sqlite3
import urllib.request
import ssl
import sys

# Google Sheets CSV export URL
SHEET_URL = "https://docs.google.com/spreadsheets/d/1G4v10KupkEqA7gn6KZ1yZmXxc07-ymPPTDX4gxfudiA/export?format=csv&gid=0"
DATABASE = 'films.db'

def parse_year_watched(year_str):
    """Parse year_watched field which might be 'Pre-2006', '2010', etc."""
    if not year_str:
        return None
    return year_str

def parse_int_or_none(value):
    """Parse integer or return None"""
    if not value or value.strip() == '':
        return None
    try:
        return int(value)
    except ValueError:
        return None

def init_database():
    """Initialize the database with the films table"""
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS films (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            order_number INTEGER,
            date_seen TEXT,
            title TEXT NOT NULL,
            letter_rating TEXT,
            score INTEGER,
            year_watched TEXT,
            location TEXT,
            format TEXT,
            release_year INTEGER,
            rotten_tomatoes TEXT,
            length_minutes INTEGER,
            rt_per_minute TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    conn.commit()
    conn.close()

def import_films():
    """Import films from Google Sheets CSV"""
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
        conn = sqlite3.connect(DATABASE)
        cursor = conn.cursor()

        # Clear existing data (optional - comment out if you want to keep existing films)
        print("Clearing existing films...")
        cursor.execute('DELETE FROM films')

        count = 0
        print("Importing films...")

        for row in csv_reader:
            # Map CSV columns to database fields
            # Note: Google Sheets has a typo "J-Rayting" instead of "J-Rating"
            order_number = parse_int_or_none(row.get('Order', ''))
            date_seen = row.get('Date Film Seen', '').strip()
            title = row.get('Film', '').strip()
            letter_rating = row.get('J-Rayting', '').strip()  # Note the typo
            score = parse_int_or_none(row.get('Score', ''))
            year_watched = parse_year_watched(row.get('Year', '').strip())
            location = row.get('Location Seen', '').strip()
            format_type = row.get('Film Format', '').strip()
            release_year = parse_int_or_none(row.get('Film Year', ''))
            rotten_tomatoes = row.get('Rotten Tomatoes', '').strip()
            length_minutes = parse_int_or_none(row.get('Film Length', ''))
            rt_per_minute = row.get('RT% per minute', '').strip()

            # Skip rows without an Order number (stats, summaries, etc.)
            if order_number is None:
                continue

            # Skip rows without a title
            if not title:
                continue

            # Insert into database
            cursor.execute('''
                INSERT INTO films (
                    order_number, date_seen, title, letter_rating, score,
                    year_watched, location, format, release_year,
                    rotten_tomatoes, length_minutes, rt_per_minute
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                order_number, date_seen, title, letter_rating, score,
                year_watched, location, format_type, release_year,
                rotten_tomatoes, length_minutes, rt_per_minute
            ))

            count += 1
            if count % 100 == 0:
                print(f"  Imported {count} films...")

        conn.commit()
        conn.close()

        print(f"\n✅ Successfully imported {count} films!")
        print(f"Database: {DATABASE}")

    except Exception as e:
        print(f"\n❌ Error importing films: {e}")
        sys.exit(1)

if __name__ == '__main__':
    import_films()
