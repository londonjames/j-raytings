#!/usr/bin/env python3
"""
Clean up format field in database - consolidate variations
"""

import sqlite3

DATABASE = 'films.db'

def cleanup_formats():
    """Consolidate format variations"""

    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()

    print("Cleaning up formats...")

    # Consolidate streaming services
    streaming_services = [
        'Netflix', 'Nefflix', 'Neflix', 'Netlix',
        'Disney+', 'Disney +', 'Disne Plus', 'Disney Plus',
        'Amazon Prime', 'Amazon Instant',
        'HBO Max', 'HBO',
        'Apple TV'
    ]

    cursor.execute(f"UPDATE films SET format = 'Streaming' WHERE format IN ({','.join('?' * len(streaming_services))})", streaming_services)
    print(f"✓ Consolidated {cursor.rowcount} streaming formats")

    # Consolidate On-Demand
    on_demand = ['iTunes', 'PPV', 'On-Demand/PPV', 'On-Demand PPV']
    cursor.execute(f"UPDATE films SET format = 'On-Demand' WHERE format IN ({','.join('?' * len(on_demand))})", on_demand)
    print(f"✓ Consolidated {cursor.rowcount} on-demand formats")

    # Consolidate TV
    cursor.execute("UPDATE films SET format = 'TV' WHERE format = 'DVR'")
    print(f"✓ Consolidated {cursor.rowcount} TV formats")

    # Fix Theatre spelling
    cursor.execute("UPDATE films SET format = 'Theatre' WHERE format = 'Theater'")
    print(f"✓ Fixed {cursor.rowcount} Theatre spellings")

    # Check location mistakes (Boston, Peninsula)
    cursor.execute("SELECT id, title, format, location FROM films WHERE format IN ('Boston', 'Peninsula')")
    location_issues = cursor.fetchall()

    if location_issues:
        print(f"\n⚠️  Found {len(location_issues)} films with location values in format field:")
        for row in location_issues:
            print(f"  - {row[1]} (ID: {row[0]}) - format: {row[2]}, location: {row[3]}")
        print("\nFixing: Setting format to 'Theatre' and keeping location as-is")

        cursor.execute("UPDATE films SET format = 'Theatre' WHERE format IN ('Boston', 'Peninsula')")
        print(f"✓ Fixed {cursor.rowcount} location mistakes")

    conn.commit()

    # Show final format counts
    cursor.execute("SELECT format, COUNT(*) as count FROM films WHERE format IS NOT NULL GROUP BY format ORDER BY count DESC")
    results = cursor.fetchall()

    print("\n📊 Final format distribution:")
    for format_name, count in results:
        print(f"  {format_name}: {count}")

    conn.close()
    print("\n✅ Format cleanup complete!")

if __name__ == '__main__':
    cleanup_formats()
