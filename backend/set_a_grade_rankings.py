#!/usr/bin/env python3
"""
Script to set custom rankings for A-grade movies.
Usage: python set_a_grade_rankings.py
Then follow the prompts to enter rankings.
"""

import sqlite3

DATABASE = 'films.db'

def get_a_grade_films():
    """Get all films with exact 'A' rating"""
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    cursor.execute('''
        SELECT id, title, score, a_grade_rank 
        FROM films 
        WHERE letter_rating = "A" 
        ORDER BY score DESC, title ASC
    ''')
    films = cursor.fetchall()
    conn.close()
    return films

def update_ranking(film_id, rank):
    """Update the a_grade_rank for a film"""
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    cursor.execute('UPDATE films SET a_grade_rank = ? WHERE id = ?', (rank, film_id))
    conn.commit()
    conn.close()

def set_rankings_interactive():
    """Interactive function to set rankings"""
    films = get_a_grade_films()
    
    print(f"\nFound {len(films)} A-grade movies:\n")
    for i, (film_id, title, score, current_rank) in enumerate(films, 1):
        rank_str = f" (current rank: {current_rank})" if current_rank else ""
        print(f"{i}. {title} (score: {score}){rank_str}")
    
    print("\n" + "="*60)
    print("Enter rankings for 17 movies (leave one unranked).")
    print("Rank 1 = best, rank 17 = lowest ranked.")
    print("Enter 'skip' to leave a movie unranked.")
    print("Enter 'quit' to exit.\n")
    
    rankings = {}
    
    for i, (film_id, title, score, current_rank) in enumerate(films, 1):
        while True:
            try:
                user_input = input(f"Rank for '{title}' (1-17, 'skip', or 'quit'): ").strip().lower()
                
                if user_input == 'quit':
                    print("\nExiting without saving changes.")
                    return
                
                if user_input == 'skip':
                    print(f"  Skipping {title}")
                    break
                
                rank = int(user_input)
                if rank < 1 or rank > 17:
                    print("  Please enter a number between 1 and 17, or 'skip'")
                    continue
                
                if rank in rankings.values():
                    print(f"  Rank {rank} is already assigned. Please choose a different rank.")
                    continue
                
                rankings[film_id] = rank
                print(f"  ✓ Assigned rank {rank} to {title}")
                break
                
            except ValueError:
                print("  Please enter a number, 'skip', or 'quit'")
    
    if not rankings:
        print("\nNo rankings were set.")
        return
    
    print(f"\n\nYou've set {len(rankings)} rankings:")
    for film_id, rank in sorted(rankings.items(), key=lambda x: x[1]):
        film = next((f for f in films if f[0] == film_id), None)
        if film:
            print(f"  Rank {rank}: {film[1]}")
    
    confirm = input("\nSave these rankings? (yes/no): ").strip().lower()
    if confirm == 'yes':
        for film_id, rank in rankings.items():
            update_ranking(film_id, rank)
        print(f"\n✅ Successfully saved {len(rankings)} rankings!")
    else:
        print("\nCancelled. No changes were saved.")

def set_rankings_from_list(rankings_list):
    """
    Set rankings from a list of tuples: [(film_title, rank), ...]
    Example: [('Jaws', 1), ('Goodfellas', 2), ...]
    """
    films = get_a_grade_films()
    film_dict = {title.lower(): (film_id, title) for film_id, title, _, _ in films}
    
    updated = 0
    for title, rank in rankings_list:
        title_lower = title.lower()
        if title_lower in film_dict:
            film_id, actual_title = film_dict[title_lower]
            update_ranking(film_id, rank)
            print(f"✓ Set rank {rank} for '{actual_title}'")
            updated += 1
        else:
            print(f"⚠ Warning: '{title}' not found in A-grade movies")
    
    print(f"\n✅ Successfully updated {updated} rankings!")

if __name__ == '__main__':
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == '--help':
        print("""
Usage:
  python set_a_grade_rankings.py
    Interactive mode - prompts for each ranking
    
  python set_a_grade_rankings.py --list
    Set rankings from code (edit script to add your rankings)
        """)
    elif len(sys.argv) > 1 and sys.argv[1] == '--list':
        # User can edit this list with their rankings
        # Format: [('Film Title', rank), ...]
        rankings_list = [
            # Add your rankings here, for example:
            # ('Jaws', 1),
            # ('Goodfellas', 2),
            # ...
        ]
        set_rankings_from_list(rankings_list)
    else:
        set_rankings_interactive()

