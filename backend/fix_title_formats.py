import sqlite3
import re
from tmdb_service import search_movie
from datetime import datetime
import time
import os

db_path = 'films.db'
log_file = f'title_fix_log_{datetime.now().strftime("%Y%m%d_%H%M%S")}.txt'

def log_message(message):
    """Write message to both console and log file"""
    print(message)
    with open(log_file, 'a', encoding='utf-8') as f:
        f.write(message + '\n')

def fix_title_format(title):
    """Convert 'Title, The' to 'The Title' and 'Title, A' to 'A Title'"""
    # Match patterns like ", The" ", A" ", An" at the end
    pattern = r'^(.+),\s+(The|A|An)$'
    match = re.match(pattern, title)

    if match:
        main_title = match.group(1)
        article = match.group(2)
        return f"{article} {main_title}"

    return title

def generate_rt_url(title):
    """Generate Rotten Tomatoes URL from movie title"""
    # Remove special characters and convert to lowercase
    slug = re.sub(r'[^\w\s-]', '', title.lower())
    # Replace spaces with underscores
    slug = re.sub(r'[\s]+', '_', slug)
    return f"https://www.rottentomatoes.com/m/{slug}"

def fix_all_titles():
    """Fix all title formats, regenerate RT links, and refresh posters"""

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # Get all films with reversed titles
    cursor.execute("""
        SELECT id, title, release_year, rt_link, poster_url
        FROM films
        WHERE title LIKE '%, The'
           OR title LIKE '%, A'
           OR title LIKE '%, An'
        ORDER BY title ASC
    """)
    films = cursor.fetchall()

    log_message("=" * 80)
    log_message(f"TITLE FORMAT FIX - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    log_message("=" * 80)
    log_message(f"Found {len(films)} films with reversed article format\n")

    stats = {
        'titles_fixed': 0,
        'rt_links_updated': 0,
        'posters_updated': 0,
        'errors': 0
    }

    for index, (film_id, old_title, release_year, old_rt_link, old_poster) in enumerate(films, 1):
        try:
            # Fix the title
            new_title = fix_title_format(old_title)

            if new_title != old_title:
                log_message(f"[{index}/{len(films)}] {old_title} → {new_title}")

                # Generate new RT link
                new_rt_link = generate_rt_url(new_title)

                # Fetch new poster from TMDB if API key available
                new_poster = old_poster
                if os.getenv('TMDB_API_KEY'):
                    try:
                        movie_data = search_movie(new_title, release_year)
                        if movie_data and movie_data.get('poster_url'):
                            new_poster = movie_data['poster_url']
                            if new_poster != old_poster:
                                log_message(f"  ✓ Updated poster")
                                stats['posters_updated'] += 1
                        time.sleep(0.25)  # Rate limiting
                    except Exception as e:
                        log_message(f"  ⚠ Could not fetch poster: {e}")

                # Update database
                cursor.execute("""
                    UPDATE films
                    SET title = ?, rt_link = ?, poster_url = ?
                    WHERE id = ?
                """, (new_title, new_rt_link, new_poster, film_id))

                conn.commit()

                stats['titles_fixed'] += 1

                if new_rt_link != old_rt_link:
                    log_message(f"  Old RT: {old_rt_link}")
                    log_message(f"  New RT: {new_rt_link}")
                    stats['rt_links_updated'] += 1

                log_message("")

        except Exception as e:
            log_message(f"[{index}/{len(films)}] ERROR: {old_title}")
            log_message(f"  {str(e)}\n")
            stats['errors'] += 1

    conn.close()

    # Final summary
    log_message("=" * 80)
    log_message("TITLE FIX COMPLETED")
    log_message("=" * 80)
    log_message(f"Titles fixed: {stats['titles_fixed']}")
    log_message(f"RT links updated: {stats['rt_links_updated']}")
    log_message(f"Posters updated: {stats['posters_updated']}")
    log_message(f"Errors: {stats['errors']}")
    log_message(f"\nLog saved to: {log_file}")
    log_message("=" * 80)

    return stats

if __name__ == '__main__':
    print("\n🎬 Fixing title formats for all films with reversed articles...")
    print("This will update titles, RT links, and posters.\n")

    stats = fix_all_titles()

    print("\n✅ Done!")
    print(f"\nSummary:")
    print(f"  - Fixed {stats['titles_fixed']} titles")
    print(f"  - Updated {stats['rt_links_updated']} RT links")
    print(f"  - Updated {stats['posters_updated']} posters")
