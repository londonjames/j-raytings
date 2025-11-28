import sqlite3
import pandas as pd

# Read original spreadsheet
original_df = pd.read_excel('original_films.xlsx')

# Connect to database
conn = sqlite3.connect('films.db')
cursor = conn.cursor()

# Get recent films (2020+) from database
cursor.execute("""
    SELECT title, release_year, rt_link
    FROM films
    WHERE release_year >= 2020
    ORDER BY release_year DESC, title
""")
db_films = cursor.fetchall()
conn.close()

# Check for mismatches
print("=" * 100)
print("VERIFYING RT LINKS: Original Spreadsheet vs Current Database")
print("=" * 100)

# Create lookup dict from original spreadsheet
# Try to find the RT link column in the spreadsheet
print("\nOriginal spreadsheet columns:")
print(original_df.columns.tolist())
print("\n")

# Look for RT link column (might be named differently)
rt_link_col = None
for col in original_df.columns:
    if 'rotten' in col.lower() or 'rt' in col.lower() or 'link' in col.lower():
        if 'http' in str(original_df[col].iloc[0]).lower() or 'rottentomatoes' in str(original_df[col].iloc[0]).lower():
            rt_link_col = col
            print(f"Found RT link column: {col}")
            break

if not rt_link_col:
    print("⚠️ Could not find RT link column in spreadsheet")
    print("\nFirst few rows:")
    print(original_df.head())
else:
    # Compare recent films
    mismatches = []
    matches = 0

    for title, year, db_link in db_films:
        # Find in original spreadsheet
        original_row = original_df[
            (original_df['Film'].str.strip() == title.strip()) &
            (original_df['Year'] == year)
        ]

        if not original_row.empty:
            original_link = original_row.iloc[0][rt_link_col]

            # Clean up links for comparison
            if pd.notna(original_link) and str(original_link).strip():
                original_link_clean = str(original_link).strip()
                db_link_clean = str(db_link).strip() if db_link else ''

                if original_link_clean != db_link_clean:
                    mismatches.append({
                        'title': title,
                        'year': year,
                        'original': original_link_clean,
                        'database': db_link_clean
                    })
                else:
                    matches += 1

    print(f"\n{'=' * 100}")
    print(f"RESULTS FOR FILMS 2020+:")
    print(f"{'=' * 100}")
    print(f"Matches: {matches}")
    print(f"MISMATCHES: {len(mismatches)}")

    if mismatches:
        print(f"\n⚠️ THESE FILMS HAVE WRONG RT LINKS IN DATABASE:")
        print(f"{'=' * 100}")
        for m in mismatches[:20]:  # Show first 20
            print(f"\n{m['title']} ({m['year']})")
            print(f"  YOUR LINK:     {m['original']}")
            print(f"  DATABASE LINK: {m['database']}")

        if len(mismatches) > 20:
            print(f"\n... and {len(mismatches) - 20} more mismatches")

    print(f"\n{'=' * 100}")
