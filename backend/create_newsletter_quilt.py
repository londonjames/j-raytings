#!/usr/bin/env python3
"""
Create a patchwork quilt image from newsletter/book cover images.
Similar to the films quilt but for the "What's the So What Newsletter" block.
"""

import sqlite3
import requests
from PIL import Image
import io
import os

OUTPUT_FILE = 'newsletter_quilt.jpg'
GRID_COLUMNS = 3  # 3 columns × 3 rows for 9 images
GRID_ROWS = 3
CELL_WIDTH = 250  # Width of each grid cell
CELL_HEIGHT = 188  # Height of each grid cell (4:3 aspect ratio - landscape)
PADDING = 0  # No padding - seamless images with no borders

# Image URLs or file paths - All 9 newsletter images
# Grid order: 0=top-left, 1=top-middle, 2=top-right, 3=middle-left, 4=middle-middle, 5=middle-right, 6=bottom-left, 7=bottom-middle, 8=bottom-right
NEWSLETTER_IMAGES = [
    'https://media.licdn.com/dms/image/v2/D4D12AQGrFXPtyoKVXw/article-cover_image-shrink_423_752/article-cover_image-shrink_423_752/0/1705199692601?e=1766016000&v=beta&t=dkPk8J9VEPw7q_7lK0FC3TitubQLBUaPQjWIw-Mc_ew',  # 0: Shark (was bottom-left)
    'https://media.licdn.com/dms/image/v2/C4D12AQHnDo8h3A4E6A/article-cover_image-shrink_600_2000/article-cover_image-shrink_600_2000/0/1613420047799?e=1766016000&v=beta&t=WZ7YN4N6QUrD5JZqP3sozgjNa_saac2er92OHCIHyoM',  # 1: top-middle (unchanged)
    'https://media.licdn.com/dms/image/v2/D4D12AQE6uIQ7lAQANg/article-cover_image-shrink_423_752/article-cover_image-shrink_423_752/0/1721802722911?e=1766016000&v=beta&t=LjAFubKnf-dUZD1DpL9QHFnj3Pv-GAbEvRnaG3CLDCo',  # 2: Split screen man (was middle-right)
    'https://media.licdn.com/dms/image/v2/C4D12AQHSxRvbXh4FfA/article-cover_image-shrink_423_752/article-cover_image-shrink_423_752/0/1618970691405?e=1766016000&v=beta&t=huEiPaY0SYYlEjwnSIBKDe-ZDRanDd36PfndhD_GX0U',  # 3: middle-left (unchanged)
    'https://media.licdn.com/dms/image/v2/C4D12AQHBut1nEY4gMg/article-cover_image-shrink_423_752/article-cover_image-shrink_423_752/0/1620883418698?e=1766016000&v=beta&t=SG5G79yf2i2keBm3ga1C0I6N7elQNclI3c4ciCeEQLM',  # 4: middle-middle (unchanged)
    'https://media.licdn.com/dms/image/v2/C4D12AQFWBG8cBN60pg/article-cover_image-shrink_423_752/article-cover_image-shrink_423_752/0/1614450089861?e=1766016000&v=beta&t=Y8WyE4ldH60sYqf0iq7qNqmBDHRy8tUiFe9UeHQQ3zw',  # 5: Was top-right, now middle-right
    'https://media.licdn.com/dms/image/v2/D4D12AQEdMrndn8NEDw/article-cover_image-shrink_600_2000/article-cover_image-shrink_600_2000/0/1702529171871?e=1766016000&v=beta&t=Oa087wensXhDx8QkYtwZ2jQga5HhBmkPXHadbgdgwZI',  # 6: bottom-middle → bottom-left (swapped)
    'https://media.licdn.com/dms/image/v2/C4D12AQE0sgTMyXwx1g/article-cover_image-shrink_720_1280/article-cover_image-shrink_720_1280/0/1624510314269?e=1766016000&v=beta&t=FnGQIk3pPQIeVQd1k7bCgi93TZOCvKYANccYVph2HkU',  # 7: Andy Grove → bottom-middle (swapped) - needs special crop
    'https://media.licdn.com/dms/image/v2/D4D12AQFFaGrrDK1eTw/article-cover_image-shrink_423_752/article-cover_image-shrink_423_752/0/1729720825647?e=1766016000&v=beta&t=L3LqpgzthONbqk3k0NQj3UVoIl7fMbXCrysWEu7Mpfc',  # 8: bottom-right (unchanged)
]

# Special handling for images that need different crop positioning
# Image at position 7 (Andy Grove) needs to show more of the top (less crop from top)
SPECIAL_CROP_IMAGES = {
    7: {'top_crop_ratio': 0.05}  # Only crop 5% from top, 95% from bottom (to show header)
}

def download_image(url_or_path):
    """Download an image from URL or load from local file"""
    try:
        if url_or_path.startswith('http://') or url_or_path.startswith('https://'):
            # Download from URL
            response = requests.get(url_or_path, timeout=10)
            response.raise_for_status()
            return Image.open(io.BytesIO(response.content))
        else:
            # Load from local file
            return Image.open(url_or_path)
    except Exception as e:
        print(f"Error loading {url_or_path}: {e}")
        return None

def create_quilt(image_sources, output_file=OUTPUT_FILE):
    """Create a patchwork quilt from newsletter images with 4:3 landscape cells"""
    print(f"Creating newsletter quilt from {len(image_sources)} images...")
    
    # Create a blank canvas with dark background (matches site theme)
    quilt_width = GRID_COLUMNS * CELL_WIDTH
    quilt_height = GRID_ROWS * CELL_HEIGHT
    quilt = Image.new('RGB', (quilt_width, quilt_height), color='#1c1c1c')  # Dark charcoal to match site
    
    downloaded = 0
    failed = 0
    
    # Image size fills cells completely (no padding - seamless)
    image_width = CELL_WIDTH
    image_height = CELL_HEIGHT
    
    # Fill grid slots - use provided images or placeholders
    total_slots = GRID_COLUMNS * GRID_ROWS
    
    for idx in range(total_slots):
        row = idx // GRID_COLUMNS
        col = idx % GRID_COLUMNS
        
        # Calculate position (no padding - seamless)
        x = col * CELL_WIDTH
        y = row * CELL_HEIGHT
        
        # Get image source if available, otherwise use placeholder
        if idx < len(image_sources):
            image_source = image_sources[idx]
            print(f"[{idx+1}/{total_slots}] Processing image {idx+1}...")
            # Load image
            img = download_image(image_source)
        else:
            print(f"[{idx+1}/{total_slots}] Using placeholder for slot {idx+1}...")
            img = None
        
        if img:
            # Convert to RGB if needed
            if img.mode != 'RGB':
                img = img.convert('RGB')
            
            # Crop and resize to fill the 4:3 landscape cell
            # Favor the top portion (where titles are) by cropping more from bottom
            original_width, original_height = img.size
            original_aspect = original_width / original_height
            target_aspect = image_width / image_height  # 4:3 = 1.33
            
            # Check if this image needs special crop handling
            special_crop = SPECIAL_CROP_IMAGES.get(idx)
            top_crop_ratio = special_crop['top_crop_ratio'] if special_crop else 0.15
            
            # Crop to match 4:3 aspect ratio, favoring top portion
            if original_aspect > target_aspect:  # Original is wider - crop width
                # Crop to center 4:3 rectangle (horizontal crop)
                crop_height = original_height
                crop_width = int(crop_height * target_aspect)
                left = (original_width - crop_width) // 2
                top = 0
                right = left + crop_width
                bottom = original_height
                img = img.crop((left, top, right, bottom))
            elif original_aspect < target_aspect:  # Original is taller - crop height
                # Crop to 4:3 rectangle, but favor top (customizable crop ratio)
                crop_width = original_width
                crop_height = int(crop_width / target_aspect)
                left = 0
                # Shift crop up: use custom top_crop_ratio (default 15% from top, 85% from bottom)
                crop_amount = original_height - crop_height
                top_crop = int(crop_amount * top_crop_ratio)  # Custom ratio (lower = show more top)
                top = top_crop
                right = original_width
                bottom = top + crop_height
                img = img.crop((left, top, right, bottom))
            # If already matching aspect ratio, no crop needed
            
            # Resize to fill the cell exactly (4:3 landscape)
            img = img.resize((image_width, image_height), Image.Resampling.LANCZOS)
            
            # Slightly desaturate to make it feel more in the background (subtle effect)
            # Convert to grayscale and blend back with original for subtle desaturation
            gray = img.convert('L').convert('RGB')
            # Blend: 85% original color, 15% grayscale for subtle desaturation
            img = Image.blend(img, gray, 0.15)
            
            # Paste directly - no offset needed since it fills the cell
            quilt.paste(img, (x, y))
            downloaded += 1
        else:
            # Create a dark placeholder
            placeholder = Image.new('RGB', (image_width, image_height), color='#2a2a2a')
            quilt.paste(placeholder, (x, y))
            failed += 1
    
    # Save the quilt
    quilt.save(output_file, 'JPEG', quality=90)
    print(f"\n✅ Newsletter quilt created: {output_file}")
    print(f"   Processed: {downloaded}")
    print(f"   Failed: {failed}")
    print(f"   Size: {quilt_width}x{quilt_height}px")
    print(f"   Grid: {GRID_COLUMNS} columns × {GRID_ROWS} rows")
    
    return output_file

if __name__ == '__main__':
    print("📰 Creating Newsletter Quilt Image")
    print("=" * 50)
    
    # Check if PIL is available
    try:
        from PIL import Image
    except ImportError:
        print("ERROR: PIL/Pillow is not installed.")
        print("Install it with: pip install Pillow")
        exit(1)
    
    # Check if images are provided
    if not NEWSLETTER_IMAGES or len(NEWSLETTER_IMAGES) == 0:
        print("\n⚠️  No images provided!")
        print("\nPlease update NEWSLETTER_IMAGES list in this script with:")
        print("  - Image URLs (http:// or https://)")
        print("  - Local file paths")
        print("\nExample:")
        print('  NEWSLETTER_IMAGES = [')
        print('      "https://example.com/image1.jpg",')
        print('      "path/to/local/image2.jpg",')
        print('      ...')
        print('  ]')
        exit(1)
    
    # Create the quilt
    create_quilt(NEWSLETTER_IMAGES)
    
    print(f"\n📸 Newsletter quilt image saved to: {OUTPUT_FILE}")
    print("   You can now use this as the background for the Newsletter button!")

