#!/usr/bin/env python3
"""
Export films with Rotten Tomatoes links to CSV

Usage:
    python3 export_with_rt_links.py
"""

import sqlite3
import csv

DATABASE = 'films.db'
OUTPUT_FILE = 'films_with_rt_links.csv'

def export_with_rt_links():
    """Export all films including RT links"""

    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

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
            genres,
            rt_link
        FROM films
        ORDER BY order_number ASC
    ''')

    films = cursor.fetchall()
    conn.close()

    with open(OUTPUT_FILE, 'w', newline='', encoding='utf-8') as csvfile:
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
            'Genres',
            'RT Link'
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
                'Genres': film['genres'] or '',
                'RT Link': film['rt_link'] or ''
            })

    print(f"✅ Exported {len(films)} films with RT links to {OUTPUT_FILE}")
    print(f"\nYou can now import this to Google Sheets to update:")
    print(f"- Updated film titles")
    print(f"- Rotten Tomatoes links (for hyperlinking)")

if __name__ == '__main__':
    export_with_rt_links()
