import sqlite3

db_path = 'films.db'
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

# IDs to delete as specified by user
ids_to_delete = [
    3022, 3532, 2093, 3380, 2648, 2652, 2651, 2409, 2425, 2158,
    2159, 2184, 3401, 2535, 3282, 2288, 2084, 3116, 3131, 2464,
    2959, 3201, 2490, 2054, 2339, 3579, 2999
]

print("=" * 100)
print("DELETING DUPLICATE ENTRIES")
print("=" * 100)
print()

for film_id in ids_to_delete:
    # Get film details before deleting
    cursor.execute("SELECT title, release_year, score FROM films WHERE id = ?", (film_id,))
    result = cursor.fetchone()

    if result:
        title, year, score = result
        print(f"Deleting ID {film_id}: {title} ({year}) - score={score}")
        cursor.execute("DELETE FROM films WHERE id = ?", (film_id,))
    else:
        print(f"⚠ ID {film_id} not found")

conn.commit()

print()
print("=" * 100)
print(f"Deleted {len(ids_to_delete)} duplicate entries")
print("=" * 100)

# Verify no more duplicates
cursor.execute("""
    SELECT COUNT(*)
    FROM (
        SELECT title, release_year, COUNT(*) as count
        FROM films
        GROUP BY title, release_year
        HAVING count > 1
    )
""")
remaining_duplicates = cursor.fetchone()[0]
print(f"Remaining duplicate groups: {remaining_duplicates}")

conn.close()
