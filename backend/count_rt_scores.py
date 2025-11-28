import sqlite3

conn = sqlite3.connect('films.db')
cursor = conn.cursor()

# Count films with RT scores
cursor.execute("SELECT COUNT(*) FROM films WHERE rotten_tomatoes IS NOT NULL AND rotten_tomatoes != ''")
with_scores = cursor.fetchone()[0]

# Count total films
cursor.execute("SELECT COUNT(*) FROM films")
total = cursor.fetchone()[0]

# Count missing scores
missing = total - with_scores

print(f"Total films: {total}")
print(f"Films with RT scores: {with_scores}")
print(f"Films missing RT scores: {missing}")
print(f"Coverage: {with_scores/total*100:.1f}%")

conn.close()
