import sqlite3
from datetime import datetime

db_path = 'films.db'
output_file = f'missing_rt_scores_{datetime.now().strftime("%Y%m%d_%H%M%S")}.txt'

conn = sqlite3.connect(db_path)
cursor = conn.cursor()

# Get all films missing RT scores
cursor.execute("""
    SELECT id, title, release_year, rt_link, poster_url
    FROM films
    WHERE rotten_tomatoes IS NULL OR rotten_tomatoes = ''
    ORDER BY release_year DESC, title ASC
""")

missing_films = cursor.fetchall()
conn.close()

print(f"Found {len(missing_films)} films missing Rotten Tomatoes scores\n")
print("=" * 80)

# Group by decade for easier analysis
by_decade = {}
unknown_year = []

for film_id, title, year, rt_link, poster in missing_films:
    if year:
        decade = (int(year) // 10) * 10
        if decade not in by_decade:
            by_decade[decade] = []
        by_decade[decade].append((film_id, title, year, rt_link, poster))
    else:
        unknown_year.append((film_id, title, year, rt_link, poster))

# Write to file and console
with open(output_file, 'w', encoding='utf-8') as f:
    header = f"FILMS MISSING ROTTEN TOMATOES SCORES - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
    separator = "=" * 80

    f.write(f"{separator}\n")
    f.write(f"{header}\n")
    f.write(f"{separator}\n")
    f.write(f"Total: {len(missing_films)} films\n\n")

    print(header)
    print(separator)

    # Print by decade
    for decade in sorted(by_decade.keys(), reverse=True):
        films = by_decade[decade]
        decade_header = f"\n{decade}s ({len(films)} films)"
        print(decade_header)
        f.write(f"{decade_header}\n")
        f.write("-" * 80 + "\n")

        for film_id, title, year, rt_link, poster in films:
            line = f"  [{year}] {title}"
            print(line)
            f.write(line + "\n")

            # Note any issues
            if not rt_link:
                issue = "    ⚠ No RT link"
                print(issue)
                f.write(issue + "\n")
            if not poster:
                issue = "    ⚠ No poster"
                print(issue)
                f.write(issue + "\n")

    # Print films with unknown years
    if unknown_year:
        unknown_header = f"\nUnknown Year ({len(unknown_year)} films)"
        print(unknown_header)
        f.write(f"\n{unknown_header}\n")
        f.write("-" * 80 + "\n")

        for film_id, title, year, rt_link, poster in unknown_year:
            line = f"  {title}"
            print(line)
            f.write(line + "\n")

            if not rt_link:
                issue = "    ⚠ No RT link"
                print(issue)
                f.write(issue + "\n")
            if not poster:
                issue = "    ⚠ No poster"
                print(issue)
                f.write(issue + "\n")

print(f"\n{separator}")
print(f"Full list saved to: {output_file}")
print(separator)

# Summary statistics
print("\nBreakdown by decade:")
for decade in sorted(by_decade.keys(), reverse=True):
    print(f"  {decade}s: {len(by_decade[decade])} films")
if unknown_year:
    print(f"  Unknown: {len(unknown_year)} films")

# Common issues
films_no_rt_link = sum(1 for _, _, _, rt_link, _ in missing_films if not rt_link)
films_no_poster = sum(1 for _, _, _, _, poster in missing_films if not poster)

print(f"\nCommon issues:")
print(f"  Missing RT link: {films_no_rt_link} films")
print(f"  Missing poster: {films_no_poster} films")
