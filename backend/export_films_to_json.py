#!/usr/bin/env python3
"""
Export all films from SQLite database to JSON file for migration to PostgreSQL
"""

import sqlite3
import json
from datetime import datetime

DATABASE = 'films.db'
OUTPUT_FILE = 'films_export.json'

def export_films():
    """Export all films to JSON"""
    try:
        conn = sqlite3.connect(DATABASE)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()

        cursor.execute('SELECT * FROM films ORDER BY id')
        films = [dict(row) for row in cursor.fetchall()]

        conn.close()

        # Write to JSON file
        with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
            json.dump(films, f, indent=2, ensure_ascii=False)

        print(f"✓ Exported {len(films)} films to {OUTPUT_FILE}")
        return films

    except Exception as e:
        print(f"✗ Error exporting films: {e}")
        return []

if __name__ == '__main__':
    films = export_films()
    print(f"\nTotal films exported: {len(films)}")
