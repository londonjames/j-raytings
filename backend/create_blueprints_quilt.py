#!/usr/bin/env python3
"""
Create a patchwork quilt image from Blueprints images.
Similar to the films and newsletter quilts but for the "Blueprints" block.
"""

import requests
from PIL import Image
import io
import os

OUTPUT_FILE = 'blueprints_quilt.jpg'
GRID_COLUMNS = 3  # 3 columns × 3 rows for 9 images
GRID_ROWS = 3
CELL_WIDTH = 250  # Width of each grid cell
CELL_HEIGHT = 188  # Height of each grid cell (4:3 aspect ratio - landscape)
PADDING = 0  # No padding - seamless images with no borders

# Image URLs - All 9 Blueprints images
# Grid order: 0=top-left, 1=top-middle, 2=top-right, 3=middle-left, 4=middle-middle, 5=middle-right, 6=bottom-left, 7=bottom-middle, 8=bottom-right
BLUEPRINTS_IMAGES = [
    'https://images.spr.so/cdn-cgi/imagedelivery/j42No7y-dcokJuNgXeA0ig/14d4fdbb-b35b-4c62-ac49-676efed97ed7/Untitled_Artwork_9/w=1920,quality=90,fit=scale-down',  # 0: top-left (was middle-left)
    'https://images.spr.so/cdn-cgi/imagedelivery/j42No7y-dcokJuNgXeA0ig/27e2c3b5-02ec-4c8c-9533-d31d55a94cae/Untitled_Artwork_60/w=1920,quality=90,fit=scale-down',  # 1: top-middle (unchanged)
    'https://images.spr.so/cdn-cgi/imagedelivery/j42No7y-dcokJuNgXeA0ig/83118d4d-c080-4482-8223-1bf51787efd0/IMG_0890/w=1920,quality=90,fit=scale-down',  # 2: top-right (was middle-middle)
    'https://images.spr.so/cdn-cgi/imagedelivery/j42No7y-dcokJuNgXeA0ig/56bd863b-ec44-4054-8dc6-13e42789b980/Untitled_Artwork_58/w=1920,quality=90,fit=scale-down',  # 3: top-right → middle-left
    'https://images.spr.so/cdn-cgi/imagedelivery/j42No7y-dcokJuNgXeA0ig/c43fe8f7-fff1-4cff-bfef-55024199d217/Untitled_Artwork_11/w=750,quality=90,fit=scale-down',  # 4: top-left → middle-middle
    'https://images.spr.so/cdn-cgi/imagedelivery/j42No7y-dcokJuNgXeA0ig/29abc44f-a827-4918-b226-cf918bc19b89/Untitled_Artwork_83/w=1920,quality=90,fit=scale-down',  # 5: middle-right (unchanged)
    None,  # Position 6 (bottom-left) - deleted, will use placeholder
    'https://images.spr.so/cdn-cgi/imagedelivery/j42No7y-dcokJuNgXeA0ig/639297ad-1844-4591-98eb-2e9bc295b0fc/Untitled_Artwork_59/w=1920,quality=90,fit=scale-down',  # 7: bottom-middle (new image)
    'https://images.spr.so/cdn-cgi/imagedelivery/j42No7y-dcokJuNgXeA0ig/0c9a8b96-e591-42f2-b456-2726d0f9984c/Untitled_Artwork_24/w=1920,quality=90,fit=scale-down',  # 8: bottom-right (unchanged)
]

# Special handling for images that need different crop positioning
SPECIAL_CROP_IMAGES = {
    # Add any special crop requirements here if needed
}

def download_image(url_or_path):
    """Download an image from URL or load from local file"""
    if url_or_path is None:
        return None
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
    """Create a patchwork quilt from Blueprints images with 4:3 landscape cells"""
    print(f"Creating Blueprints quilt from {len(image_sources)} images...")
    
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
    print(f"\n✅ Blueprints quilt created: {output_file}")
    print(f"   Processed: {downloaded}")
    print(f"   Failed: {failed}")
    print(f"   Size: {quilt_width}x{quilt_height}px")
    print(f"   Grid: {GRID_COLUMNS} columns × {GRID_ROWS} rows")
    
    return output_file

if __name__ == '__main__':
    print("🔷 Creating Blueprints Quilt Image")
    print("=" * 50)
    
    # Check if PIL is available
    try:
        from PIL import Image
    except ImportError:
        print("ERROR: PIL/Pillow is not installed.")
        print("Install it with: pip install Pillow")
        exit(1)
    
    # Check if images are provided
    if not BLUEPRINTS_IMAGES or len(BLUEPRINTS_IMAGES) == 0:
        print("\n⚠️  No images provided!")
        exit(1)
    
    # Create the quilt
    create_quilt(BLUEPRINTS_IMAGES)
    
    print(f"\n📸 Blueprints quilt image saved to: {OUTPUT_FILE}")
    print("   You can now use this as the background for the Blueprints button!")

