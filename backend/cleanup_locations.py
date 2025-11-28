import pandas as pd
import sqlite3

# Read the Excel file with correct headers
file_path = '/Users/jamesraybould/Downloads/@londonjames - films, books, and songs (1).xlsx'
df = pd.read_excel(file_path, header=1)
df = df.iloc[:, 1:]  # Drop first empty column

# Define location cleanup mapping
location_mapping = {
    # Peninsula variations
    'Peninsula\n': 'Peninsula',
    'Pensinsula': 'Peninsula',
    'Pensinula': 'Peninsula',
    'Peninusula': 'Peninsula',
    'Peninsulat': 'Peninsula',
    'Peninsual': 'Peninsula',

    # Portola Valley variations
    'Portola Valley\n': 'Portola Valley',

    # Plane/Flight variations
    'Flight': 'Plane',
    'Plane\n': 'Plane',

    # LA variations - all to Los Angeles
    'LA': 'Los Angeles',
    'SoCal': 'Los Angeles',

    # DC variations
    'D.C.': 'DC',

    # Minor typos
    'Redwooc City': 'Redwood City',
    'Famly camp': 'Family camp',
    'New Zeal': 'New Zealand',
}

# Apply the mapping
print("Cleaning up locations...")
print("="*80)

# Show before counts for locations being changed
changed_locations = set(location_mapping.keys()) | set(location_mapping.values())
before_counts = df['Location Seen'].value_counts()
print("\nBEFORE cleanup:")
for loc in sorted(changed_locations):
    if loc in before_counts:
        print(f"  {loc:50} {before_counts[loc]:>6}")

# Apply the mapping
df['Location Seen'] = df['Location Seen'].replace(location_mapping)

# Show after counts
after_counts = df['Location Seen'].value_counts()
print("\nAFTER cleanup:")
for loc in sorted(changed_locations):
    if loc in after_counts:
        print(f"  {loc:50} {after_counts[loc]:>6}")

# Update the database
print("\n" + "="*80)
print("Updating database...")
db_path = '/Users/jamesraybould/Documents/film-tracker/backend/films.db'
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

# Get all films from database
cursor.execute("SELECT id, title, order_number FROM films")
db_films = cursor.fetchall()

updates_made = 0
films_not_found = []

# Match films by title and order number, then update location
for _, row in df.iterrows():
    title = row['Film']
    order_num = row['Order']
    location = row['Location Seen']

    if pd.notna(location):  # Only update if location exists
        # Find matching film in database by order number (most reliable)
        cursor.execute(
            "UPDATE films SET location = ? WHERE order_number = ?",
            (location, order_num)
        )
        if cursor.rowcount > 0:
            updates_made += 1
        else:
            films_not_found.append((order_num, title))

conn.commit()

print(f"Updated {updates_made} films with cleaned locations")
if films_not_found:
    print(f"\nWarning: {len(films_not_found)} films from Excel not found in database")
    if len(films_not_found) <= 10:
        for order_num, title in films_not_found[:10]:
            print(f"  Order {order_num}: {title}")

# Show final location counts in database
cursor.execute("""
    SELECT location, COUNT(*) as count
    FROM films
    WHERE location IS NOT NULL AND location != ''
    GROUP BY location
    ORDER BY count DESC
""")
results = cursor.fetchall()

print("\n" + "="*80)
print("FINAL location counts in database:")
for location, count in results:
    print(f"{location:50} {count:>6}")

print(f"\nTotal distinct locations in database: {len(results)}")

conn.close()
print("\nDone! Locations have been cleaned up.")
