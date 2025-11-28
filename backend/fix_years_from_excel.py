import sqlite3
import pandas as pd
from datetime import datetime
import os

db_path = 'films.db'
excel_path = '/Users/jamesraybould/Downloads/@londonjames - films, books, and songs (1).xlsx'
log_file = f'year_fix_from_excel_{datetime.now().strftime("%Y%m%d_%H%M%S")}.txt'

def log_message(message):
    """Write message to both console and log file"""
    print(message)
    with open(log_file, 'a', encoding='utf-8') as f:
        f.write(message + '\n')

def normalize_title(title):
    """Normalize title for comparison"""
    # Remove extra spaces, convert to lowercase
    return ' '.join(str(title).lower().strip().split())

def extract_year(year_value):
    """Extract 4-digit year from various formats"""
    if pd.isna(year_value):
        return None

    year_str = str(year_value).strip()

    # Try to extract first 4-digit number
    import re
    match = re.search(r'\b(19|20)\d{2}\b', year_str)
    if match:
        return int(match.group())

    # Try converting directly to int
    try:
        year = int(float(year_str))
        if 1900 <= year <= 2030:
            return year
    except:
        pass

    return None

def main():
    log_message("=" * 80)
    log_message(f"FIXING YEARS FROM EXCEL SOURCE - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    log_message("=" * 80)

    # Read Excel file
    log_message(f"\nReading Excel file: {excel_path}")
    try:
        df = pd.read_excel(excel_path, sheet_name='all films', header=1)
        log_message(f"Found {len(df)} films in Excel\n")
    except Exception as e:
        log_message(f"Error reading Excel: {e}")
        return

    # Connect to database
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # Get all films from database
    cursor.execute("SELECT id, title, release_year FROM films")
    db_films = cursor.fetchall()

    log_message(f"Found {len(db_films)} films in database\n")

    # Create lookup dict from Excel
    excel_lookup = {}
    for _, row in df.iterrows():
        title = row.get('Film')
        year = row.get('Film Year')

        if pd.notna(title):
            normalized = normalize_title(title)
            extracted_year = extract_year(year)
            excel_lookup[normalized] = {
                'original_title': title,
                'year': extracted_year
            }

    log_message(f"Created lookup for {len(excel_lookup)} Excel titles\n")
    log_message("=" * 80)
    log_message("COMPARING YEARS\n")

    stats = {
        'matched': 0,
        'year_fixed': 0,
        'year_added': 0,
        'not_found_in_excel': 0,
        'no_year_in_excel': 0
    }

    fixes = []

    for film_id, db_title, db_year in db_films:
        normalized_db = normalize_title(db_title)

        if normalized_db in excel_lookup:
            stats['matched'] += 1
            excel_data = excel_lookup[normalized_db]
            excel_year = excel_data['year']

            if excel_year:
                # Compare years
                if db_year != excel_year:
                    if db_year:
                        log_message(f"[MISMATCH] {db_title}")
                        log_message(f"  DB year: {db_year} → Excel year: {excel_year}")
                        stats['year_fixed'] += 1
                    else:
                        log_message(f"[MISSING] {db_title}")
                        log_message(f"  Adding year: {excel_year}")
                        stats['year_added'] += 1

                    fixes.append((excel_year, film_id, db_title))
            else:
                stats['no_year_in_excel'] += 1
        else:
            stats['not_found_in_excel'] += 1

    log_message("\n" + "=" * 80)
    log_message("SUMMARY")
    log_message("=" * 80)
    log_message(f"Matched films: {stats['matched']}")
    log_message(f"Years to fix: {stats['year_fixed']}")
    log_message(f"Years to add: {stats['year_added']}")
    log_message(f"No year in Excel: {stats['no_year_in_excel']}")
    log_message(f"Not found in Excel: {stats['not_found_in_excel']}")

    # Apply fixes
    if fixes:
        log_message(f"\n" + "=" * 80)
        log_message(f"APPLYING {len(fixes)} FIXES")
        log_message("=" * 80)

        for new_year, film_id, title in fixes:
            cursor.execute("UPDATE films SET release_year = ? WHERE id = ?", (new_year, film_id))
            log_message(f"✓ Updated {title} → {new_year}")

        conn.commit()
        log_message(f"\nSuccessfully updated {len(fixes)} films")
    else:
        log_message("\nNo fixes needed!")

    conn.close()

    log_message("\n" + "=" * 80)
    log_message(f"Log saved to: {log_file}")
    log_message("=" * 80)

    return stats

if __name__ == '__main__':
    stats = main()
    print(f"\n✅ Done!")
    if stats:
        print(f"Fixed/added years for {stats['year_fixed'] + stats['year_added']} films")
