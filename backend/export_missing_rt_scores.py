import sqlite3
from datetime import datetime

db_path = 'films.db'
output_file = f'missing_rt_scores_with_links_{datetime.now().strftime("%Y%m%d_%H%M%S")}.txt'

conn = sqlite3.connect(db_path)
cursor = conn.cursor()

# Get all films missing RT scores with their J-Rayting and RT links
cursor.execute("""
    SELECT title, release_year, score, rt_link
    FROM films
    WHERE rotten_tomatoes IS NULL OR rotten_tomatoes = ''
    ORDER BY
        CASE WHEN rt_link IS NOT NULL AND rt_link != '' THEN 0 ELSE 1 END,
        release_year DESC,
        title ASC
""")

missing_films = cursor.fetchall()
conn.close()

# Separate films with and without RT links
with_links = []
without_links = []

for title, year, score, rt_link in missing_films:
    if rt_link and rt_link.strip():
        with_links.append((title, year, score, rt_link))
    else:
        without_links.append((title, year, score, rt_link))

# Write to file
with open(output_file, 'w', encoding='utf-8') as f:
    header = f"FILMS MISSING ROTTEN TOMATOES SCORES - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
    separator = "=" * 100

    f.write(f"{separator}\n")
    f.write(f"{header}\n")
    f.write(f"{separator}\n\n")
    f.write(f"Total films missing RT scores: {len(missing_films)}\n")
    f.write(f"  - WITH RT links: {len(with_links)} films (just need to add score manually)\n")
    f.write(f"  - WITHOUT RT links: {len(without_links)} films (need both link and score)\n\n")

    # Section 1: Films WITH RT links (priority - just add score)
    if with_links:
        f.write(f"\n{separator}\n")
        f.write(f"✅ FILMS WITH RT LINKS ({len(with_links)} films)\n")
        f.write(f"These already have links - just need to add the RT score from the link\n")
        f.write(f"{separator}\n\n")

        for title, year, score, rt_link in with_links:
            f.write(f"Film: {title} ({year})\n")
            f.write(f"Your Rating: {score if score else 'N/A'}\n")
            f.write(f"RT Link: {rt_link}\n")
            f.write(f"RT Score: _____%  ← ADD MANUALLY\n")
            f.write(f"\n")

    # Section 2: Films WITHOUT RT links
    if without_links:
        f.write(f"\n{separator}\n")
        f.write(f"⚠️  FILMS WITHOUT RT LINKS ({len(without_links)} films)\n")
        f.write(f"These need both RT link AND score to be researched\n")
        f.write(f"{separator}\n\n")

        for title, year, score, rt_link in without_links:
            f.write(f"Film: {title} ({year})\n")
            f.write(f"Your Rating: {score if score else 'N/A'}\n")
            f.write(f"RT Link: MISSING - needs research\n")
            f.write(f"RT Score: _____%\n")
            f.write(f"\n")

    f.write(f"\n{separator}\n")
    f.write(f"END OF LIST\n")
    f.write(f"{separator}\n")

print(f"✅ Report generated: {output_file}\n")
print(f"Summary:")
print(f"  Total missing RT scores: {len(missing_films)}")
print(f"  WITH RT links: {len(with_links)} films (priority)")
print(f"  WITHOUT RT links: {len(without_links)} films")
print(f"\nThe films WITH links are listed first - those are the easiest to complete!")
