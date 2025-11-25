#!/usr/bin/env python3
"""
Script to set custom rankings for A-grade movies in production (PostgreSQL).
This script connects to the production database via DATABASE_URL environment variable.
"""

import os
import psycopg2
from urllib.parse import urlparse

# Get DATABASE_URL from environment (Railway sets this)
DATABASE_URL = os.getenv('DATABASE_URL')

if not DATABASE_URL:
    print("ERROR: DATABASE_URL environment variable not set.")
    print("This script must be run in an environment with DATABASE_URL (e.g., Railway).")
    exit(1)

def get_db_connection():
    """Get database connection from DATABASE_URL"""
    result = urlparse(DATABASE_URL)
    conn = psycopg2.connect(
        database=result.path[1:],  # Remove leading '/'
        user=result.username,
        password=result.password,
        host=result.hostname,
        port=result.port
    )
    return conn

def get_a_grade_films():
    """Get all films with exact 'A' rating"""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('''
        SELECT id, title, score, a_grade_rank 
        FROM films 
        WHERE letter_rating = 'A' 
        ORDER BY score DESC, title ASC
    ''')
    films = cursor.fetchall()
    conn.close()
    return films

def update_ranking(film_id, rank):
    """Update the a_grade_rank for a film"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Check if column exists first
    cursor.execute("""
        SELECT column_name 
        FROM information_schema.columns 
        WHERE table_name='films' AND column_name='a_grade_rank'
    """)
    if not cursor.fetchone():
        print("ERROR: a_grade_rank column does not exist in production database.")
        print("Please ensure the database migration has run.")
        conn.close()
        return False
    
    cursor.execute('UPDATE films SET a_grade_rank = %s WHERE id = %s', (rank, film_id))
    conn.commit()
    conn.close()
    return True

def set_rankings_from_list(rankings_list):
    """
    Set rankings from a list of tuples: [(film_title, rank), ...]
    """
    films = get_a_grade_films()
    film_dict = {title.lower(): (film_id, title) for film_id, title, _, _ in films}
    
    print(f"Found {len(films)} A-grade movies in database\n")
    
    updated = 0
    not_found = []
    
    for title, rank in rankings_list:
        title_lower = title.lower()
        if title_lower in film_dict:
            film_id, actual_title = film_dict[title_lower]
            if update_ranking(film_id, rank):
                print(f"✓ Set rank {rank} for '{actual_title}'")
                updated += 1
            else:
                print(f"✗ Failed to update '{actual_title}'")
        else:
            not_found.append(title)
            print(f"⚠ Warning: '{title}' not found in A-grade movies")
    
    if not_found:
        print(f"\n⚠ Could not find {len(not_found)} movies:")
        for title in not_found:
            print(f"  - {title}")
    
    print(f"\n✅ Successfully updated {updated} rankings!")
    return updated

if __name__ == '__main__':
    # The 18 A-grade movies with custom rankings
    # Rank 1 = best, rank 18 = lowest ranked
    rankings_list = [
        ('Jaws', 1),
        ('Goodfellas', 2),
        ('Social Network, The', 3),
        ('Parasite', 4),
        ('Stand By Me', 5),
        ('Ferris Bueller\'s Day Off', 6),
        ('Back to the Future', 7),
        ('12 Angry Men', 8),
        ('About A Boy', 9),
        ('All About Eve', 10),
        ('American President, The', 11),
        ('Beautiful Mind, A', 12),
        ('Braveheart', 13),
        ('Forrest Gump', 14),
        ('Mystic River', 15),
        ('Philadelphia Story, The', 16),
        ('Shawshank Redemption, The', 17),
        ('Sting, The', 18),
    ]
    
    print("Setting A-grade rankings in production database...")
    print("=" * 60)
    set_rankings_from_list(rankings_list)
    print("=" * 60)
    print("Done!")

