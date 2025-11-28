import sqlite3

db_path = 'films.db'
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

print("=" * 100)
print("J-RAYTINGS DATABASE STATUS REPORT")
print("=" * 100)

# Total films
cursor.execute("SELECT COUNT(*) FROM films")
total_films = cursor.fetchone()[0]
print(f"\n📊 TOTAL FILMS: {total_films}")

# Missing ratings (J-Rayting score)
cursor.execute("SELECT COUNT(*) FROM films WHERE score IS NULL OR score = ''")
missing_ratings = cursor.fetchone()[0]
print(f"\n⭐ YOUR RATINGS (J-Rayting):")
print(f"   Films with ratings: {total_films - missing_ratings}")
print(f"   Films missing ratings: {missing_ratings}")
if missing_ratings > 0:
    cursor.execute("SELECT title, release_year FROM films WHERE score IS NULL OR score = '' ORDER BY release_year DESC LIMIT 10")
    examples = cursor.fetchall()
    print(f"\n   Examples of films missing your rating:")
    for title, year in examples[:5]:
        print(f"     - {title} ({year})")

# Missing RT links
cursor.execute("SELECT COUNT(*) FROM films WHERE rt_link IS NULL OR rt_link = ''")
missing_rt_links = cursor.fetchone()[0]
print(f"\n🔗 ROTTEN TOMATOES LINKS:")
print(f"   Films with RT links: {total_films - missing_rt_links}")
print(f"   Films missing RT links: {missing_rt_links}")

# Missing RT scores
cursor.execute("SELECT COUNT(*) FROM films WHERE rotten_tomatoes IS NULL OR rotten_tomatoes = ''")
missing_rt_scores = cursor.fetchone()[0]
print(f"\n🍅 ROTTEN TOMATOES SCORES:")
print(f"   Films with RT scores: {total_films - missing_rt_scores} ({((total_films - missing_rt_scores) / total_films * 100):.1f}%)")
print(f"   Films missing RT scores: {missing_rt_scores}")

# Missing posters
cursor.execute("SELECT COUNT(*) FROM films WHERE poster_url IS NULL OR poster_url = '' OR poster_url = 'PLACEHOLDER'")
missing_posters = cursor.fetchone()[0]
print(f"\n🖼️  MOVIE POSTERS:")
print(f"   Films with posters: {total_films - missing_posters}")
print(f"   Films missing posters: {missing_posters}")
if missing_posters > 0:
    cursor.execute("SELECT title, release_year FROM films WHERE poster_url IS NULL OR poster_url = '' OR poster_url = 'PLACEHOLDER' ORDER BY release_year DESC LIMIT 10")
    examples = cursor.fetchall()
    print(f"\n   Films missing posters:")
    for title, year in examples:
        print(f"     - {title} ({year})")

# Duplicates
cursor.execute("""
    SELECT title, release_year, COUNT(*) as count
    FROM films
    GROUP BY title, release_year
    HAVING count > 1
    ORDER BY count DESC, title
""")
duplicates = cursor.fetchall()
total_duplicate_entries = sum(count - 1 for _, _, count in duplicates)

print(f"\n🔄 DUPLICATE ENTRIES:")
print(f"   Unique films with duplicates: {len(duplicates)}")
print(f"   Total extra duplicate entries: {total_duplicate_entries}")

if duplicates:
    print(f"\n   Duplicate films:")
    for title, year, count in duplicates[:15]:
        print(f"     - {title} ({year}) - {count} copies")
    if len(duplicates) > 15:
        print(f"     ... and {len(duplicates) - 15} more")

# Summary
print(f"\n{'=' * 100}")
print("QUICK SUMMARY:")
print(f"{'=' * 100}")
print(f"  Total Films: {total_films}")
print(f"  Missing YOUR ratings: {missing_ratings}")
print(f"  Missing RT links: {missing_rt_links}")
print(f"  Missing RT scores: {missing_rt_scores}")
print(f"  Missing posters: {missing_posters}")
print(f"  Duplicate entries to clean: {total_duplicate_entries}")
print(f"{'=' * 100}")

conn.close()
