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
            
            # Crop and resize to fill the 4:3 landscape cell
            # Favor the top portion (where titles are) by cropping more from bottom
            original_width, original_height = poster_img.size
            original_aspect = original_width / original_height
            target_aspect = image_width / image_height  # 4:3 = 1.33
            
            # Crop to match 4:3 aspect ratio, favoring top portion
            if original_aspect > target_aspect:  # Original is wider - crop width
                # Crop to center 4:3 rectangle (horizontal crop)
                crop_height = original_height
                crop_width = int(crop_height * target_aspect)
                left = (original_width - crop_width) // 2
                top = 0
                right = left + crop_width
                bottom = original_height
                poster_img = poster_img.crop((left, top, right, bottom))
            elif original_aspect < target_aspect:  # Original is taller - crop height
                # Crop to 4:3 rectangle, but favor top (crop 85% from bottom, 15% from top)
                crop_width = original_width
                crop_height = int(crop_width / target_aspect)
                left = 0
                # Shift crop up: take 15% from top, 85% from bottom
                crop_amount = original_height - crop_height
                top_crop = int(crop_amount * 0.15)  # Only 15% from top
                top = top_crop
                right = original_width
                bottom = top + crop_height
                poster_img = poster_img.crop((left, top, right, bottom))
            # If already matching aspect ratio, no crop needed
            
            # Resize to fill the cell exactly (4:3 landscape)
            poster_img = poster_img.resize((image_width, image_height), Image.Resampling.LANCZOS)
            
            # Slightly desaturate to make it feel more in the background (subtle effect)
            # Convert to grayscale and blend back with original for subtle desaturation
            gray = poster_img.convert('L').convert('RGB')
            # Blend: 85% original color, 15% grayscale for subtle desaturation
            poster_img = Image.blend(poster_img, gray, 0.15)
            
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

