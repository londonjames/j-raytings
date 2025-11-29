#!/usr/bin/env python3
"""
Update book types from abbreviated format to readable format:
- NF/BUSIN → "Non-fiction: Business"
- NF/SOC → "Non-fiction: Social"
- NF/SPORT → "Non-fiction: Sport"
- NF/BIO → "Non-fiction: Bio"
- NF/POL → "Non-fiction: Politics"
- NF/TRUECRIME → "Non-fiction: True Crime"
- FICT → "Fiction"
- NON-FICT → "Non-fiction"
"""

import sqlite3
import os

DATABASE = 'films.db'

# Mapping from old format to new format
TYPE_MAPPING = {
    'NF/BUSIN': 'Non-fiction: Business',
    'NF/SOC': 'Non-fiction: Social',
    'NF/SPORT': 'Non-fiction: Sport',
    'NF/BIO': 'Non-fiction: Bio',
    'NF/POL': 'Non-fiction: Politics',
    'NF/TRUECRIME': 'Non-fiction: True Crime',
    'FICT': 'Fiction',
    'NON-FICT': 'Non-fiction'
}

def update_book_types():
    """Update book types in the database"""
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    
    print("=" * 80)
    print("UPDATING BOOK TYPES")
    print("=" * 80)
    print()
    
    # Show current distribution
    print("Current type distribution:")
    cursor.execute("SELECT type, COUNT(*) FROM books WHERE type IS NOT NULL GROUP BY type ORDER BY COUNT(*) DESC")
    current_types = cursor.fetchall()
    for type_val, count in current_types:
        print(f"  {type_val}: {count} books")
    print()
    
    # Update each type
    total_updated = 0
    for old_type, new_type in TYPE_MAPPING.items():
        cursor.execute("SELECT COUNT(*) FROM books WHERE type = ?", (old_type,))
        count = cursor.fetchone()[0]
        
        if count > 0:
            cursor.execute("UPDATE books SET type = ? WHERE type = ?", (new_type, old_type))
            print(f"✓ Updated {count} books: '{old_type}' → '{new_type}'")
            total_updated += count
    
    conn.commit()
    
    # Show new distribution
    print()
    print("New type distribution:")
    cursor.execute("SELECT type, COUNT(*) FROM books WHERE type IS NOT NULL GROUP BY type ORDER BY COUNT(*) DESC")
    new_types = cursor.fetchall()
    for type_val, count in new_types:
        print(f"  {type_val}: {count} books")
    
    print()
    print(f"✓ Total books updated: {total_updated}")
    print("=" * 80)
    
    conn.close()

if __name__ == '__main__':
    update_book_types()

