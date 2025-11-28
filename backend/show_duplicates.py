import sqlite3

db_path = 'films.db'
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

# Find all duplicates
cursor.execute("""
    SELECT title, release_year
    FROM films
    GROUP BY title, release_year
    HAVING COUNT(*) > 1
    ORDER BY title, release_year
""")
duplicate_groups = cursor.fetchall()

print("=" * 100)
print("DUPLICATE ENTRIES - Choose which IDs to DELETE")
print("=" * 100)
print()

for idx, (title, year) in enumerate(duplicate_groups, 1):
    # Get all entries for this film
    cursor.execute("""
        SELECT id, score, rotten_tomatoes, poster_url
        FROM films
        WHERE title = ? AND release_year = ?
        ORDER BY id
    """, (title, year))

    entries = cursor.fetchall()

    # Compact format: show IDs with their key data
    entry_parts = []
    for film_id, score, rt_score, poster in entries:
        score_str = f"score={score}" if score else "no score"
        rt_str = f"RT={rt_score}" if rt_score else "no RT"
        poster_str = "poster" if poster and poster != 'PLACEHOLDER' else "no poster"
        entry_parts.append(f"ID {film_id} ({score_str}, {rt_str}, {poster_str})")

    print(f"{idx:2}. {title} ({year})")
    print(f"    {' vs '.join(entry_parts)}")

print()
print("=" * 100)
print(f"Total: {len(duplicate_groups)} duplicate groups with {sum(1 for _ in duplicate_groups)} extra entries")
print("=" * 100)

conn.close()
