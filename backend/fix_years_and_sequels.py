import sqlite3
import re
from tmdb_service import search_movie
from datetime import datetime
import time
import os

db_path = 'films.db'
log_file = f'year_sequel_fix_log_{datetime.now().strftime("%Y%m%d_%H%M%S")}.txt'

def log_message(message):
    """Write message to both console and log file"""
    print(message)
    with open(log_file, 'a', encoding='utf-8') as f:
        f.write(message + '\n')

# Known sequel mappings - TMDB uses these formats
SEQUEL_MAPPINGS = {
    # Star Wars
    'Star Wars I': ('Star Wars: Episode I - The Phantom Menace', 1999),
    'Star Wars II': ('Star Wars: Episode II - Attack of the Clones', 2002),
    'Star Wars III': ('Star Wars: Episode III - Revenge of the Sith', 2005),

    # Spider-Man (Raimi trilogy)
    'Spider-Man I': ('Spider-Man', 2002),
    'Spider-Man II': ('Spider-Man 2', 2004),
    'Spider-Man III': ('Spider-Man 3', 2007),

    # The Godfather
    'The Godfather II': ('The Godfather Part II', 1974),
    'The Godfather III': ('The Godfather Part III', 1990),

    # Rocky
    'Rocky II': ('Rocky II', 1979),
    'Rocky III': ('Rocky III', 1982),
    'Rocky IV': ('Rocky IV', 1985),
    'Rocky V': ('Rocky V', 1990),

    # Die Hard
    'Die Hard I': ('Die Hard', 1988),
    'Die Hard II': ('Die Hard 2', 1990),
    'Die Hard III': ('Die Hard with a Vengeance', 1995),

    # Naked Gun
    'Naked Gun I': ('The Naked Gun: From the Files of Police Squad!', 1988),
    'Naked Gun II': ('The Naked Gun 2½: The Smell of Fear', 1991),
    'Naked Gun III': ('Naked Gun 33⅓: The Final Insult', 1994),

    # Austin Powers
    'Austin Powers I': ('Austin Powers: International Man of Mystery', 1997),
    'Austin Powers II': ('Austin Powers: The Spy Who Shagged Me', 1999),
    'Austin Powers III': ('Austin Powers in Goldmember', 2002),

    # Toy Story
    'Toy Story I': ('Toy Story', 1995),
    'Toy Story II': ('Toy Story 2', 1999),
    'Toy Story III': ('Toy Story 3', 2010),

    # Crocodile Dundee
    'Crocodile Dundee I': ('Crocodile Dundee', 1986),
    'Crocodile Dundee II': ('Crocodile Dundee II', 1988),

    # Superman
    'Superman I': ('Superman', 1978),
    'Superman II': ('Superman II', 1980),
    'Superman III': ('Superman III', 1983),

    # Bill and Ted
    "Bill and Ted's Excellent Adventure I": ("Bill & Ted's Excellent Adventure", 1989),
    "Bill and Ted's Bogus Journey II": ("Bill & Ted's Bogus Journey", 1991),
}

def has_roman_numeral_suffix(title):
    """Check if title ends with Roman numeral (I, II, III, IV, V)"""
    return re.search(r'\s+[IVX]+$', title) is not None

def fix_years_and_sequels():
    """Fix release years and sequel formatting"""

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # Get all films that might need fixing
    # 1. Films with Roman numerals
    # 2. Specific known problem films
    cursor.execute("""
        SELECT id, title, release_year, rotten_tomatoes
        FROM films
        WHERE title LIKE '% I'
           OR title LIKE '% II'
           OR title LIKE '% III'
           OR title LIKE '% IV'
           OR title LIKE '% V'
           OR title = '1917'
           OR rotten_tomatoes IS NULL OR rotten_tomatoes = ''
        ORDER BY title ASC
    """)
    films = cursor.fetchall()

    log_message("=" * 80)
    log_message(f"YEAR AND SEQUEL FIX - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    log_message("=" * 80)
    log_message(f"Found {len(films)} films to check\n")

    stats = {
        'titles_fixed': 0,
        'years_fixed': 0,
        'skipped': 0,
        'errors': 0
    }

    for index, (film_id, title, release_year, rt_score) in enumerate(films, 1):
        try:
            new_title = title
            new_year = release_year
            changed = False

            # Check if it's a known sequel mapping
            if title in SEQUEL_MAPPINGS:
                new_title, new_year = SEQUEL_MAPPINGS[title]
                log_message(f"[{index}/{len(films)}] {title} ({release_year})")
                log_message(f"  → {new_title} ({new_year})")
                changed = True
                stats['titles_fixed'] += 1
                if new_year != release_year:
                    stats['years_fixed'] += 1

            # For other films, check TMDB for correct year
            elif not rt_score or title == '1917':
                if os.getenv('TMDB_API_KEY'):
                    try:
                        log_message(f"[{index}/{len(films)}] Checking TMDB for: {title} ({release_year})")
                        movie_data = search_movie(title, release_year)

                        if movie_data:
                            tmdb_year = movie_data.get('release_year')
                            tmdb_title = movie_data.get('title')

                            # Update year if different
                            if tmdb_year and tmdb_year != release_year:
                                new_year = tmdb_year
                                log_message(f"  ✓ Year updated: {release_year} → {new_year}")
                                stats['years_fixed'] += 1
                                changed = True

                            # Update title if TMDB has better format (but be careful)
                            if tmdb_title and tmdb_title != title:
                                # Only update if it's a clear improvement
                                if has_roman_numeral_suffix(title) and not has_roman_numeral_suffix(tmdb_title):
                                    new_title = tmdb_title
                                    log_message(f"  ✓ Title updated: {title} → {new_title}")
                                    stats['titles_fixed'] += 1
                                    changed = True
                        else:
                            log_message(f"  ⚠ Not found on TMDB")

                        time.sleep(0.25)  # Rate limiting

                    except Exception as e:
                        log_message(f"  ⚠ TMDB error: {e}")
                else:
                    log_message(f"[{index}/{len(films)}] Skipping {title} (no TMDB API key)")
                    stats['skipped'] += 1

            # Update database if anything changed
            if changed:
                cursor.execute("""
                    UPDATE films
                    SET title = ?, release_year = ?
                    WHERE id = ?
                """, (new_title, new_year, film_id))
                conn.commit()
                log_message("")

        except Exception as e:
            log_message(f"[{index}/{len(films)}] ERROR: {title}")
            log_message(f"  {str(e)}\n")
            stats['errors'] += 1

    conn.close()

    # Final summary
    log_message("=" * 80)
    log_message("FIX COMPLETED")
    log_message("=" * 80)
    log_message(f"Titles fixed: {stats['titles_fixed']}")
    log_message(f"Years fixed: {stats['years_fixed']}")
    log_message(f"Skipped: {stats['skipped']}")
    log_message(f"Errors: {stats['errors']}")
    log_message(f"\nLog saved to: {log_file}")
    log_message("=" * 80)

    return stats

if __name__ == '__main__':
    print("\n🎬 Fixing release years and sequel formats...\n")

    if not os.getenv('TMDB_API_KEY'):
        print("⚠ Warning: TMDB_API_KEY not set. Will only fix known sequel mappings.")
        print("Set TMDB_API_KEY to enable year verification.\n")

    stats = fix_years_and_sequels()

    print("\n✅ Done!")
    print(f"\nSummary:")
    print(f"  - Fixed {stats['titles_fixed']} titles")
    print(f"  - Fixed {stats['years_fixed']} years")
    if stats['skipped'] > 0:
        print(f"  - Skipped {stats['skipped']} films")
