#!/usr/bin/env python3
"""
Consolidate book categories according to new naming scheme
"""
from import_books import get_db

def consolidate_categories():
    db = get_db()
    cursor = db.cursor()
    
    # Mapping of old categories to new categories
    category_mapping = {
        'FICT': 'Fiction',
        'Fiction': 'Fiction',
        'NF/BUSIN': 'Non-Fict: Biz',
        'NF/SOC': 'Non-Fict: Soc.',
        'NF/SPORT': 'Non-Fict: Sport',
        'NF/POL': 'Non-Fict: Pol.',
        'NF/BIO': 'Non-Fict: Other',
        'NF/TRUECRIME': 'Non-Fict: Other',
        'NON-FICT': 'Non-Fict: Other',
        'Non-fiction: Social': 'Non-Fict: Soc.',
        'Non-fiction: Sport': 'Non-Fict: Sport',
    }
    
    print("=" * 80)
    print("CONSOLIDATING BOOK CATEGORIES")
    print("=" * 80)
    print()
    
    # Show current counts
    print("Current categories:")
    cursor.execute('SELECT DISTINCT type FROM books WHERE type IS NOT NULL AND type != "" ORDER BY type')
    current_types = cursor.fetchall()
    for (type_val,) in current_types:
        cursor.execute('SELECT COUNT(*) FROM books WHERE type = ?', (type_val,))
        count = cursor.fetchone()[0]
        print(f'  {type_val}: {count} books')
    print()
    
    # Show mapping
    print("Category mapping:")
    for old, new in sorted(category_mapping.items()):
        cursor.execute('SELECT COUNT(*) FROM books WHERE type = ?', (old,))
        count = cursor.fetchone()[0]
        if count > 0:
            print(f'  {old} → {new} ({count} books)')
    print()
    
    # Update categories
    updated_count = 0
    for old_category, new_category in category_mapping.items():
        cursor.execute('SELECT COUNT(*) FROM books WHERE type = ?', (old_category,))
        count = cursor.fetchone()[0]
        if count > 0:
            cursor.execute('UPDATE books SET type = ? WHERE type = ?', (new_category, old_category))
            updated_count += cursor.rowcount
            print(f'  ✓ Updated {count} books: {old_category} → {new_category}')
    
    db.commit()
    print()
    print(f"Total books updated: {updated_count}")
    print()
    
    # Show new counts
    print("=" * 80)
    print("UPDATED CATEGORY COUNTS")
    print("=" * 80)
    cursor.execute('SELECT DISTINCT type FROM books WHERE type IS NOT NULL AND type != "" ORDER BY type')
    new_types = cursor.fetchall()
    total = 0
    for (type_val,) in new_types:
        cursor.execute('SELECT COUNT(*) FROM books WHERE type = ?', (type_val,))
        count = cursor.fetchone()[0]
        total += count
        print(f'  {type_val}: {count} books')
    print()
    print(f'Total: {total} books')
    print()
    print("✓ Category consolidation complete!")
    
    db.close()

if __name__ == '__main__':
    consolidate_categories()
