import sqlite3
import os
from tmdb_service import search_movie, get_movie_details
import time
from datetime import datetime

# Configuration
db_path = 'films.db'
log_file = f'poster_refresh_log_{datetime.now().strftime("%Y%m%d_%H%M%S")}.txt'
rate_limit_delay = 0.25  # 250ms between requests to respect TMDB rate limits

def log_message(message):
    """Write message to both console and log file"""
    print(message)
    with open(log_file, 'a', encoding='utf-8') as f:
        f.write(message + '\n')

def refresh_all_posters():
    """Re-fetch all posters from TMDB"""

    if not os.getenv('TMDB_API_KEY'):
        log_message("ERROR: TMDB_API_KEY not found in environment variables")
        return

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # Get all films
    cursor.execute("""
        SELECT id, title, release_year, poster_url
        FROM films
        ORDER BY order_number ASC
    """)
    films = cursor.fetchall()

    total_films = len(films)
    log_message("=" * 80)
    log_message(f"POSTER REFRESH STARTED - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    log_message("=" * 80)
    log_message(f"Total films to process: {total_films}\n")

    stats = {
        'updated': 0,
        'unchanged': 0,
        'not_found': 0,
        'errors': 0
    }

    for index, (film_id, title, release_year, old_poster_url) in enumerate(films, 1):
        progress = f"[{index}/{total_films}]"

        try:
            # Search for the movie on TMDB
            movie_data = search_movie(title, release_year)

            if movie_data and movie_data.get('poster_url'):
                new_poster_url = movie_data['poster_url']

                # Only update if the poster URL changed
                if new_poster_url != old_poster_url:
                    cursor.execute(
                        "UPDATE films SET poster_url = ? WHERE id = ?",
                        (new_poster_url, film_id)
                    )
                    conn.commit()

                    log_message(f"{progress} UPDATED: {title} ({release_year})")
                    log_message(f"  OLD: {old_poster_url}")
                    log_message(f"  NEW: {new_poster_url}\n")
                    stats['updated'] += 1
                else:
                    # Poster already correct
                    if index % 50 == 0:  # Log every 50th unchanged film
                        log_message(f"{progress} Unchanged: {title} ({release_year})")
                    stats['unchanged'] += 1
            else:
                # No poster found on TMDB
                log_message(f"{progress} NOT FOUND: {title} ({release_year})")
                stats['not_found'] += 1

            # Rate limiting
            time.sleep(rate_limit_delay)

        except Exception as e:
            log_message(f"{progress} ERROR: {title} ({release_year})")
            log_message(f"  Error: {str(e)}\n")
            stats['errors'] += 1

    conn.close()

    # Final summary
    log_message("\n" + "=" * 80)
    log_message("POSTER REFRESH COMPLETED")
    log_message("=" * 80)
    log_message(f"Total processed: {total_films}")
    log_message(f"Updated: {stats['updated']}")
    log_message(f"Unchanged: {stats['unchanged']}")
    log_message(f"Not found: {stats['not_found']}")
    log_message(f"Errors: {stats['errors']}")
    log_message(f"\nLog saved to: {log_file}")
    log_message("=" * 80)

    return stats

if __name__ == '__main__':
    print("\n🎬 Starting poster refresh for all films...")
    print("This will take a few minutes (rate limited to respect TMDB API).\n")

    stats = refresh_all_posters()

    print("\n✅ Done! Check the log file for details.")
