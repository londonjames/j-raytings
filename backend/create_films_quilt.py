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
GRID_COLUMNS = 3  # 3 columns × 3 rows for 9 films (more space per poster)
GRID_ROWS = 3
CELL_WIDTH = 250  # Width of each grid cell (larger for better visibility)
CELL_HEIGHT = 188  # Height of each grid cell (4:3 aspect ratio - landscape)
PADDING = 0  # No padding - seamless posters with no borders

def get_top_films(limit=9):
    """Get top films with The Godfather and Hoop Dreams first, then A-grade ranking"""
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    # Get all films with posters
    cursor.execute('''
        SELECT id, title, poster_url, letter_rating, score, a_grade_rank
        FROM films
        WHERE poster_url IS NOT NULL AND poster_url != ''
        ORDER BY 
            CASE 
                WHEN title LIKE '%Godfather%' AND title NOT LIKE '%Part II%' AND title NOT LIKE '%Part III%' THEN 0
                WHEN title = 'Hoop Dreams' THEN 1
                WHEN letter_rating = 'A' AND a_grade_rank IS NOT NULL THEN a_grade_rank + 1
                ELSE 999
            END,
            score DESC,
            title ASC
        LIMIT ?
    ''', (limit + 3,))  # Get a few extra in case we need to filter
    
    films = cursor.fetchall()
    conn.close()
    
    # Separate The Godfather and Hoop Dreams, then get the rest
    priority_films = []
    other_films = []
    
    for film in films:
        title = film['title']
        if 'Godfather' in title and 'Part II' not in title and 'Part III' not in title:
            priority_films.insert(0, film)  # The Godfather first
        elif title == 'Hoop Dreams':
            priority_films.append(film)  # Hoop Dreams second
        else:
            other_films.append(film)
    
    # Combine: priority films first, then others up to limit
    result = priority_films + other_films[:limit - len(priority_films)]
    return result[:limit]

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
    """Create a patchwork quilt from film posters with 4:3 landscape cells"""
    print(f"Creating quilt from {len(films)} films...")
    
    # Create a blank canvas with dark background (matches site theme)
    quilt_width = GRID_COLUMNS * CELL_WIDTH
    quilt_height = GRID_ROWS * CELL_HEIGHT
    quilt = Image.new('RGB', (quilt_width, quilt_height), color='#1c1c1c')  # Dark charcoal to match site
    
    downloaded = 0
    failed = 0
    
    # Image size fills cells completely (no padding - seamless)
    image_width = CELL_WIDTH
    image_height = CELL_HEIGHT
    
    for idx, film in enumerate(films):
        row = idx // GRID_COLUMNS
        col = idx % GRID_COLUMNS
        
        # Calculate position (no padding - seamless)
        x = col * CELL_WIDTH
        y = row * CELL_HEIGHT
        
        print(f"[{idx+1}/{len(films)}] Processing: {film['title']}")
        
        # Download poster
        poster_img = download_image(film['poster_url'])
        
        if poster_img:
            # Convert to RGB if needed
            if poster_img.mode != 'RGB':
                poster_img = poster_img.convert('RGB')
            
            # Crop and resize to fill the square cell completely (no gaps)
            original_width, original_height = poster_img.size
            aspect_ratio = original_width / original_height
            
            # Calculate crop to make it square, then resize to fill cell
            if aspect_ratio > 1:  # Wider than tall - crop width to make square
                # Crop to center square
                crop_size = original_height
                left = (original_width - crop_size) // 2
                top = 0
                right = left + crop_size
                bottom = original_height
                poster_img = poster_img.crop((left, top, right, bottom))
            elif aspect_ratio < 1:  # Taller than wide - crop height to make square
                # Crop to center square
                crop_size = original_width
                left = 0
                top = (original_height - crop_size) // 2
                right = original_width
                bottom = top + crop_size
                poster_img = poster_img.crop((left, top, right, bottom))
            # If already square, no crop needed
            
            # Resize to fill the cell exactly (4:3 landscape)
            poster_img = poster_img.resize((image_width, image_height), Image.Resampling.LANCZOS)
            
            # Paste directly - no offset needed since it fills the cell
            quilt.paste(poster_img, (x, y))
            downloaded += 1
        else:
            # Create a dark placeholder
            placeholder = Image.new('RGB', (image_width, image_height), color='#2a2a2a')
            quilt.paste(placeholder, (x, y))
            failed += 1
    
    # Save the quilt
    quilt.save(output_file, 'JPEG', quality=90)
    print(f"\n✅ Quilt created: {output_file}")
    print(f"   Downloaded: {downloaded}")
    print(f"   Failed: {failed}")
    print(f"   Size: {quilt_width}x{quilt_height}px")
    print(f"   Grid: {GRID_COLUMNS} columns × {GRID_ROWS} rows")
    
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
    
    # Get top films (9 total)
    films = get_top_films(9)
    
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

