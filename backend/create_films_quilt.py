#!/usr/bin/env python3
"""
Create a patchwork quilt image from the top 20 films' posters.
This will download posters and arrange them in a grid layout.
"""

import sqlite3
import requests
from PIL import Image
import io
import os
from urllib.parse import urlparse

DATABASE = 'films.db'
OUTPUT_FILE = 'films_quilt.jpg'
GRID_COLUMNS = 5  # 5 columns = 4 rows for 20 films
GRID_ROWS = 4
POSTER_SIZE = 200  # Size of each poster in the quilt

def get_top_films(limit=20):
    """Get top films sorted by rating (A-grade with custom ranking first)"""
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    # Get all films
    cursor.execute('''
        SELECT id, title, poster_url, letter_rating, score, a_grade_rank
        FROM films
        WHERE poster_url IS NOT NULL AND poster_url != ''
        ORDER BY 
            CASE 
                WHEN letter_rating = 'A' AND a_grade_rank IS NOT NULL THEN a_grade_rank
                ELSE 999
            END,
            score DESC,
            title ASC
        LIMIT ?
    ''', (limit,))
    
    films = cursor.fetchall()
    conn.close()
    return films

def download_image(url):
    """Download an image from URL"""
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        return Image.open(io.BytesIO(response.content))
    except Exception as e:
        print(f"Error downloading {url}: {e}")
        return None

def create_quilt(films, output_file=OUTPUT_FILE):
    """Create a patchwork quilt from film posters"""
    print(f"Creating quilt from {len(films)} films...")
    
    # Create a blank canvas
    quilt_width = GRID_COLUMNS * POSTER_SIZE
    quilt_height = GRID_ROWS * POSTER_SIZE
    quilt = Image.new('RGB', (quilt_width, quilt_height), color='#1c1c1c')
    
    downloaded = 0
    failed = 0
    
    for idx, film in enumerate(films):
        row = idx // GRID_COLUMNS
        col = idx % GRID_COLUMNS
        
        x = col * POSTER_SIZE
        y = row * POSTER_SIZE
        
        print(f"[{idx+1}/{len(films)}] Processing: {film['title']}")
        
        # Download poster
        poster_img = download_image(film['poster_url'])
        
        if poster_img:
            # Resize to fit the grid cell
            poster_img = poster_img.resize((POSTER_SIZE, POSTER_SIZE), Image.Resampling.LANCZOS)
            # Paste onto quilt
            quilt.paste(poster_img, (x, y))
            downloaded += 1
        else:
            # Create a placeholder
            placeholder = Image.new('RGB', (POSTER_SIZE, POSTER_SIZE), color='#2a2a2a')
            quilt.paste(placeholder, (x, y))
            failed += 1
    
    # Save the quilt
    quilt.save(output_file, 'JPEG', quality=85)
    print(f"\n✅ Quilt created: {output_file}")
    print(f"   Downloaded: {downloaded}")
    print(f"   Failed: {failed}")
    print(f"   Size: {quilt_width}x{quilt_height}px")
    
    return output_file

if __name__ == '__main__':
    print("🎬 Creating Films Quilt Image")
    print("=" * 50)
    
    # Check if PIL is available
    try:
        from PIL import Image
    except ImportError:
        print("ERROR: PIL/Pillow is not installed.")
        print("Install it with: pip install Pillow")
        exit(1)
    
    # Get top films
    films = get_top_films(20)
    
    if not films:
        print("No films found with posters!")
        exit(1)
    
    print(f"\nFound {len(films)} films with posters")
    print("\nTop films:")
    for i, film in enumerate(films[:10], 1):
        print(f"  {i}. {film['title']}")
    
    # Create the quilt
    create_quilt(films)
    
    print(f"\n📸 Quilt image saved to: {OUTPUT_FILE}")
    print("   You can now use this as the background for the Films button!")

