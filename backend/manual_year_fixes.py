#!/usr/bin/env python3
"""
Manual fixes for films with known incorrect years
"""
import sqlite3

conn = sqlite3.connect('films.db')
cursor = conn.cursor()

# Manual corrections for films where TMDB gives wrong matches
manual_fixes = {
    '48 Hours': 1982,  # Eddie Murphy film
    '6 Days and 7 Nights': 1998,  # Harrison Ford film
    'Bladerunner': 1982,  # Blade Runner original
    'Crouching Tiger, Hidden Dragon': 2000,
    'Dumb & Dumber': 1994,
    'Ever After': 1998,
    'Face Off': 1997,  # John Travolta/Nicolas Cage
    'Father\'s Day': 1997,  # Robin Williams
    'Footloose': 1984,  # Original (we have the 2011 remake already)
    'Harry Potter and the Deathly Hallows: Part 2': 2011,  # This is actually correct!
    'Little Women': 1994,  # Winona Ryder version (watched Pre-2006)
    'Palo Alto': 2007,  # Or could be 2013
    'Scream II': 1997,  # Scream 2
    'Scream: The Inside Story': 2010,  # Documentary
    'Teenage Mutant Ninja Turtles': 1990,  # Original film
    'The Jungle Book': 1967,  # Already fixed
    'The Practice': 1997,  # TV series started 1997
    'Thirteen': 2003,  # Already fixed
    'Three Amigos': 1986,  # Already fixed
    'Trespass': 1992,  # Ice-T/Bill Paxton film
    'Wall St': 1987,  # Wall Street
    'War Games': 1983,  # WarGames
    'When Harry Met Sally': 1989,
    'Y Tu Mama Tambien': 2001,
    'Black Widow': 2021,  # Marvel film - this IS from 2021, so mark watched year as wrong
    'Mission: Impossible - The Final Reckoning': 2025,  # This is upcoming, year_watched must be wrong
}

print("=" * 100)
print("MANUAL YEAR FIXES")
print("=" * 100)
print()

updated = 0

for title, correct_year in manual_fixes.items():
    cursor.execute("SELECT id, release_year FROM films WHERE title = ?", (title,))
    result = cursor.fetchone()

    if result:
        film_id, current_year = result
        if current_year != correct_year:
            print(f"{title}: {current_year} → {correct_year}")
            cursor.execute("UPDATE films SET release_year = ? WHERE id = ?", (correct_year, film_id))
            updated += 1
        else:
            print(f"{title}: Already correct ({correct_year})")
    else:
        print(f"⚠ {title}: Not found in database")

conn.commit()
conn.close()

print()
print("=" * 100)
print(f"Updated {updated} films")
print("=" * 100)
