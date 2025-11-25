#!/usr/bin/env python3
"""
Migration script to add a_grade_rank column to films table.
This allows custom ranking of A-grade movies.
"""

import sqlite3
import os

DATABASE = 'films.db'

def add_a_grade_rank_column():
    """Add a_grade_rank column to films table if it doesn't exist"""
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    
    # Check if column already exists
    cursor.execute("PRAGMA table_info(films)")
    columns = [column[1] for column in cursor.fetchall()]
    
    if 'a_grade_rank' not in columns:
        print("Adding a_grade_rank column to films table...")
        cursor.execute('ALTER TABLE films ADD COLUMN a_grade_rank INTEGER')
        conn.commit()
        print("✅ Successfully added a_grade_rank column!")
    else:
        print("✅ a_grade_rank column already exists.")
    
    conn.close()

if __name__ == '__main__':
    add_a_grade_rank_column()

