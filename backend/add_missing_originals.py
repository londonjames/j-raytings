#!/usr/bin/env python3
"""
Add the original Road House (1989) and Footloose (1984) films
"""
import sqlite3
import os
from tmdb_service import search_movie, get_movie_details

db_path = 'films.db'
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

# Films to add
films_to_add = [
    {
        'title': 'Road House',
        'release_year': 1989,
        'score': 14,  # B+
        'letter_rating': 'B+',
        'year_watched': 'Pre-2006'
    },
    {
        'title': 'Footloose',
        'release_year': 1984,
        'score': 10,  # B-
        'letter_rating': 'B-',
        'year_watched': 'Pre-2006'
    }
]

print("=" * 100)
print("ADDING MISSING ORIGINAL FILMS")
print("=" * 100)
print()

for film_data in films_to_add:
    title = film_data['title']
    release_year = film_data['release_year']

    # Check if it already exists
    cursor.execute("""
        SELECT id, title, release_year
        FROM films
        WHERE title = ? AND release_year = ?
    """, (title, release_year))

    existing = cursor.fetchone()

    if existing:
        print(f"⚠ {title} ({release_year}) already exists (ID: {existing[0]})")
        continue

    print(f"Adding {title} ({release_year})...")

    # Fetch metadata from TMDB
    poster_url = None
    genres = None
    length_minutes = None
    rotten_tomatoes = None

    try:
        movie_data = search_movie(title, release_year)

        if movie_data:
            poster_url = movie_data.get('poster_url')
            genres = movie_data.get('genres')

            tmdb_id = movie_data.get('tmdb_id')
            if tmdb_id:
                details = get_movie_details(tmdb_id)
                if details:
                    length_minutes = details.get('runtime')

            print(f"  ✓ Fetched TMDB metadata")
            print(f"    Poster: {'✓' if poster_url else '✗'}")
            print(f"    Genres: {genres if genres else 'None'}")
            print(f"    Runtime: {length_minutes if length_minutes else 'None'} min")
    except Exception as e:
        print(f"  ⚠ Error fetching TMDB data: {e}")

    # Generate RT link
    slug = title.lower().replace(' ', '_')
    rt_link = f"https://www.rottentomatoes.com/m/{slug}"

    # Insert the film
    cursor.execute("""
        INSERT INTO films (
            title, release_year, score, letter_rating, year_watched,
            poster_url, genres, length_minutes, rt_link
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        title,
        release_year,
        film_data['score'],
        film_data['letter_rating'],
        film_data['year_watched'],
        poster_url,
        genres,
        length_minutes,
        rt_link
    ))

    film_id = cursor.lastrowid
    print(f"  ✓ Added with ID {film_id}")
    print()

conn.commit()
conn.close()

print("=" * 100)
print("COMPLETE")
print("=" * 100)
