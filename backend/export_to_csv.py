#!/usr/bin/env python3
"""
Export films from database to CSV format (compatible with Google Sheets)

Usage:
    python export_to_csv.py

This will create 'films_export.csv' that you can upload to Google Sheets
"""

import sqlite3
import csv
from datetime import datetime

DATABASE = 'films.db'
OUTPUT_FILE = 'films_export.csv'

def export_to_csv():
    """Export all films to CSV format matching Google Sheets structure"""

    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    # Get all films ordered by order_number
    cursor.execute('''
        SELECT
            order_number,
            date_seen,
            title,
            letter_rating,
            score,
            year_watched,
            location,
            format,
            release_year,
            rotten_tomatoes,
            length_minutes,
            rt_per_minute,
            poster_url,
            genres
        FROM films
        ORDER BY order_number ASC
    ''')

    films = cursor.fetchall()
    conn.close()

    # Write to CSV
    with open(OUTPUT_FILE, 'w', newline='', encoding='utf-8') as csvfile:
        # Define columns (matching your Google Sheet structure)
        fieldnames = [
            'Order #',
            'Date Seen',
            'Title',
            'Letter Rating',
            'Score',
            'Year Watched',
            'Location',
            'Format',
            'Release Year',
            'Rotten Tomatoes',
            'Length (Minutes)',
            'RT/Minute',
            'Poster URL',
            'Genres'
        ]

        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()

        for film in films:
            writer.writerow({
                'Order #': film['order_number'] or '',
                'Date Seen': film['date_seen'] or '',
                'Title': film['title'] or '',
                'Letter Rating': film['letter_rating'] or '',
                'Score': film['score'] or '',
                'Year Watched': film['year_watched'] or '',
                'Location': film['location'] or '',
                'Format': film['format'] or '',
                'Release Year': film['release_year'] or '',
                'Rotten Tomatoes': film['rotten_tomatoes'] or '',
                'Length (Minutes)': film['length_minutes'] or '',
                'RT/Minute': film['rt_per_minute'] or '',
                'Poster URL': film['poster_url'] or '',
                'Genres': film['genres'] or ''
            })

    print(f"✅ Exported {len(films)} films to {OUTPUT_FILE}")
    print(f"\nTo update Google Sheets:")
    print(f"1. Open your Google Sheet")
    print(f"2. File → Import")
    print(f"3. Upload → Select '{OUTPUT_FILE}'")
    print(f"4. Import location: Replace current sheet")
    print(f"5. Click 'Import data'")

if __name__ == '__main__':
    export_to_csv()
