#!/usr/bin/env python3
"""
Export only specific columns from database to update Google Sheets

This exports: Order #, Release Year, Rotten Tomatoes, Length (Minutes)
Use this when you only want to update these columns without changing film titles.

Usage:
    python3 export_selective_columns.py
"""

import sqlite3
import csv

DATABASE = 'films.db'
OUTPUT_FILE = 'films_selective_export.csv'

def export_selective_columns():
    """Export only specific columns for selective Google Sheets update"""

    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    # Get only the columns we want to update
    cursor.execute('''
        SELECT
            order_number,
            release_year,
            rotten_tomatoes,
            length_minutes
        FROM films
        ORDER BY order_number ASC
    ''')

    films = cursor.fetchall()
    conn.close()

    # Write to CSV
    with open(OUTPUT_FILE, 'w', newline='', encoding='utf-8') as csvfile:
        fieldnames = [
            'Order #',
            'Release Year',
            'Rotten Tomatoes',
            'Length (Minutes)'
        ]

        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()

        for film in films:
            writer.writerow({
                'Order #': film['order_number'] or '',
                'Release Year': film['release_year'] or '',
                'Rotten Tomatoes': film['rotten_tomatoes'] or '',
                'Length (Minutes)': film['length_minutes'] or ''
            })

    print(f"✅ Exported {len(films)} films to {OUTPUT_FILE}")
    print(f"\nColumns exported: Order #, Release Year, Rotten Tomatoes, Length (Minutes)")
    print(f"\n📋 To update Google Sheets:")
    print(f"1. Open your Google Sheet")
    print(f"2. Create a new temporary sheet (click + at bottom)")
    print(f"3. File → Import → Upload '{OUTPUT_FILE}'")
    print(f"4. Import location: 'Insert new sheet(s)'")
    print(f"5. Use VLOOKUP to update your main sheet:")
    print(f"   In main sheet column I (Release Year): =VLOOKUP(A2,Sheet2!A:B,2,FALSE)")
    print(f"   In main sheet column J (Rotten Tomatoes): =VLOOKUP(A2,Sheet2!A:C,3,FALSE)")
    print(f"   In main sheet column K (Length): =VLOOKUP(A2,Sheet2!A:D,4,FALSE)")
    print(f"6. Copy the formulas down for all rows")
    print(f"7. Copy → Paste Special → Values only to convert formulas to values")
    print(f"8. Delete the temporary sheet")

if __name__ == '__main__':
    export_selective_columns()
