import sqlite3
import csv

db_path = 'films.db'

# Get all films with duplicate titles that were affected by fix_title_formats.py
affected_titles_with_the = [
    "The Armstrong Lie", "The Manchurian Candidate", "The Running Man"
]

conn = sqlite3.connect(db_path)
cursor = conn.cursor()

# Get all duplicate title films
cursor.execute("""
    SELECT f.title, f.release_year, f.rotten_tomatoes, f.rt_link, f.score
    FROM films f
    WHERE f.title IN (
        SELECT title FROM films GROUP BY title HAVING COUNT(*) > 1
    )
    ORDER BY f.title, f.release_year
""")

duplicates = cursor.fetchall()
conn.close()

# Categorize
high_risk_with_scores = []
high_risk_without_scores = []
other_duplicates = []

for title, year, rt_score, rt_link, user_score in duplicates:
    is_affected = title in affected_titles_with_the

    if is_affected:
        if rt_score and rt_score.strip():
            high_risk_with_scores.append((title, year, rt_score, rt_link, user_score))
        else:
            high_risk_without_scores.append((title, year, rt_score, rt_link, user_score))
    else:
        other_duplicates.append((title, year, rt_score, rt_link, user_score))

print("=" * 100)
print("DUPLICATE TITLE FILMS - RT LINK VERIFICATION NEEDED")
print("=" * 100)

print(f"\n🔴 HIGH RISK - Affected by fix_title_formats.py & HAVE RT scores:")
print(f"   These films had RT links regenerated and may be pointing to wrong film")
print("-" * 100)
for title, year, rt_score, rt_link, user_score in high_risk_with_scores:
    print(f"  {title} ({year}) - RT: {rt_score} - Link: {rt_link}")

print(f"\n\n🟡 MEDIUM RISK - Other duplicate titles (NOT affected by script):")
print(f"   These were not touched by fix_title_formats.py but should still be verified")
print("-" * 100)
for title, year, rt_score, rt_link, user_score in other_duplicates:
    status = f"RT: {rt_score}" if rt_score else "NO RT SCORE"
    print(f"  {title} ({year}) - {status} - Link: {rt_link if rt_link else 'NO LINK'}")

print("\n" + "=" * 100)
print(f"Summary:")
print(f"  High-risk with scores (check these first!): {len(high_risk_with_scores)}")
print(f"  Other duplicates: {len(other_duplicates)}")
print("=" * 100)

# Create CSV for high-risk ones
if high_risk_with_scores:
    output_file = '/Users/jamesraybould/Desktop/verify_duplicate_rt_links.csv'

    with open(output_file, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(['Film Title', 'Year', 'Current RT Score', 'Current RT Link', 'Verified RT Link (if wrong)', 'Correct RT Score (if wrong)'])

        for title, year, rt_score, rt_link, user_score in high_risk_with_scores:
            writer.writerow([title, year, rt_score, rt_link, '', ''])

    print(f"\n✅ CSV created: {output_file}")
    print("   Use this to verify and correct RT links for duplicate-title films")
