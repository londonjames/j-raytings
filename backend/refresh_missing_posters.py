import sqlite3
from tmdb_service import search_movie
from datetime import datetime
import time
import os

db_path = 'films.db'
log_file = f'refresh_missing_posters_{datetime.now().strftime("%Y%m%d_%H%M%S")}.txt'

def log_message(message):
    """Write message to both console and log file"""
    print(message)
    with open(log_file, 'a', encoding='utf-8') as f:
        f.write(message + '\n')

def refresh_missing_posters():
    """Refresh posters for films missing RT scores"""

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # Get all films missing RT scores
    cursor.execute("""
        SELECT id, title, release_year, poster_url
        FROM films
        WHERE rotten_tomatoes IS NULL OR rotten_tomatoes = ''
        ORDER BY release_year DESC
    """)
    films = cursor.fetchall()

    log_message("=" * 80)
    log_message(f"REFRESH POSTERS FOR FILMS MISSING RT SCORES - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    log_message("=" * 80)
    log_message(f"Found {len(films)} films missing RT scores\n")

    stats = {
        'posters_updated': 0,
        'already_correct': 0,
        'not_found': 0,
        'errors': 0
    }

    if not os.getenv('TMDB_API_KEY'):
        log_message("⚠ TMDB_API_KEY not set. Exiting.")
        return stats

    for index, (film_id, title, release_year, old_poster) in enumerate(films, 1):
        try:
            log_message(f"[{index}/{len(films)}] {title} ({release_year})")

            movie_data = search_movie(title, release_year)

            if movie_data and movie_data.get('poster_url'):
                new_poster = movie_data['poster_url']

                if new_poster != old_poster:
                    cursor.execute("""
                        UPDATE films
                        SET poster_url = ?
                        WHERE id = ?
                    """, (new_poster, film_id))
                    conn.commit()

                    log_message(f"  ✓ Updated poster")
                    stats['posters_updated'] += 1
                else:
                    log_message(f"  - Poster already correct")
                    stats['already_correct'] += 1
            else:
                log_message(f"  ✗ Not found on TMDB")
                stats['not_found'] += 1

            time.sleep(0.25)  # Rate limiting

        except Exception as e:
            log_message(f"  ⚠ Error: {e}")
            stats['errors'] += 1

    conn.close()

    # Final summary
    log_message("\n" + "=" * 80)
    log_message("POSTER REFRESH COMPLETED")
    log_message("=" * 80)
    log_message(f"Posters updated: {stats['posters_updated']}")
    log_message(f"Already correct: {stats['already_correct']}")
    log_message(f"Not found: {stats['not_found']}")
    log_message(f"Errors: {stats['errors']}")
    log_message(f"\nLog saved to: {log_file}")
    log_message("=" * 80)

    return stats

if __name__ == '__main__':
    print("\n🎬 Refreshing posters for films missing RT scores...\n")

    stats = refresh_missing_posters()

    print("\n✅ Done!")
    print(f"\nSummary:")
    print(f"  - Updated {stats['posters_updated']} posters")
    print(f"  - Already correct: {stats['already_correct']}")
    print(f"  - Not found: {stats['not_found']}")
