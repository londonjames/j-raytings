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
GRID_COLUMNS = 5  # 5 columns = 3 rows for 15 films
GRID_ROWS = 3
CELL_SIZE = 200  # Size of each grid cell
PADDING = 15  # White space padding around each image

def get_top_films(limit=15):
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
    ''', (limit + 2,))  # Get a few extra in case we need to filter
    
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
    """Create a patchwork quilt from film posters with maintained aspect ratios"""
    print(f"Creating quilt from {len(films)} films...")
    
    # Create a blank canvas with white background
    quilt_width = GRID_COLUMNS * CELL_SIZE
    quilt_height = GRID_ROWS * CELL_SIZE
    quilt = Image.new('RGB', (quilt_width, quilt_height), color='white')
    
    downloaded = 0
    failed = 0
    
    # Calculate image size (cell size minus padding on both sides)
    image_size = CELL_SIZE - (PADDING * 2)
    
    for idx, film in enumerate(films):
        row = idx // GRID_COLUMNS
        col = idx % GRID_COLUMNS
        
        # Calculate position with padding
        x = col * CELL_SIZE + PADDING
        y = row * CELL_SIZE + PADDING
        
        print(f"[{idx+1}/{len(films)}] Processing: {film['title']}")
        
        # Download poster
        poster_img = download_image(film['poster_url'])
        
        if poster_img:
            # Convert to RGB if needed
            if poster_img.mode != 'RGB':
                poster_img = poster_img.convert('RGB')
            
            # Maintain aspect ratio - resize to fit within the padded area
            original_width, original_height = poster_img.size
            aspect_ratio = original_width / original_height
            
            # Calculate new dimensions maintaining aspect ratio
            if aspect_ratio > 1:  # Wider than tall
                new_width = image_size
                new_height = int(image_size / aspect_ratio)
            else:  # Taller than wide or square
                new_height = image_size
                new_width = int(image_size * aspect_ratio)
            
            # Resize maintaining aspect ratio
            poster_img = poster_img.resize((new_width, new_height), Image.Resampling.LANCZOS)
            
            # Center the image in the cell
            offset_x = (image_size - new_width) // 2
            offset_y = (image_size - new_height) // 2
            
            # Paste onto quilt
            quilt.paste(poster_img, (x + offset_x, y + offset_y))
            downloaded += 1
        else:
            # Create a placeholder with padding
            placeholder = Image.new('RGB', (image_size, image_size), color='#e0e0e0')
            quilt.paste(placeholder, (x, y))
            failed += 1
    
    # Save the quilt
    quilt.save(output_file, 'JPEG', quality=90)
    print(f"\n✅ Quilt created: {output_file}")
    print(f"   Downloaded: {downloaded}")
    print(f"   Failed: {failed}")
    print(f"   Size: {quilt_width}x{quilt_height}px")
    print(f"   Padding: {PADDING}px around each image")
    
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
    
    # Get top films (15 total)
    films = get_top_films(15)
    
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

