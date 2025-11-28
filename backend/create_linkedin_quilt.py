#!/usr/bin/env python3
"""
Create/update the LinkedIn Posts quilt image.
This script can work with the existing quilt image and replace specific positions,
or create a new one from scratch with updated images and more vibrant background.
"""

import requests
from PIL import Image, ImageEnhance, ImageDraw, ImageFont
import io
import os
import numpy as np

OUTPUT_FILE = '../frontend/public/linkedin-posts-quilt.jpg'
QUILTS_DIR = '../Quilts'
GRID_COLUMNS = 3
GRID_ROWS = 3
CELL_WIDTH = 250
CELL_HEIGHT = 188
PADDING = 0

# More vibrant background color - using a warmer, more saturated color
# Instead of gray (#7a8075), let's use a vibrant blue-teal from the palette
VIBRANT_BG_COLOR = '#5a9a9a'  # Teal from color palette - more vibrant than gray

def download_image(url_or_path):
    """Download an image from URL or load from local file"""
    try:
        if url_or_path.startswith('http://') or url_or_path.startswith('https://'):
            response = requests.get(url_or_path, timeout=10)
            response.raise_for_status()
            return Image.open(io.BytesIO(response.content))
        else:
            return Image.open(url_or_path)
    except Exception as e:
        print(f"Error loading {url_or_path}: {e}")
        return None

def enhance_image_vibrancy(img, saturation_factor=1.2, brightness_factor=1.05):
    """Enhance image vibrancy"""
    enhancer = ImageEnhance.Color(img)
    img = enhancer.enhance(saturation_factor)
    enhancer = ImageEnhance.Brightness(img)
    img = enhancer.enhance(brightness_factor)
    return img

def enhance_quilt_vibrancy(quilt):
    """Enhance overall vibrancy of the quilt image - minimal enhancement to avoid washing out"""
    # Very minimal enhancement to avoid making image too bright/white
    enhancer = ImageEnhance.Color(quilt)
    quilt = enhancer.enhance(1.05)  # Small saturation increase
    enhancer = ImageEnhance.Contrast(quilt)
    quilt = enhancer.enhance(1.05)  # Small contrast increase
    # Don't increase brightness - it's making things too white
    return quilt

def change_icon_colors_to_linkedin_blue(quilt):
    """Change icon and verb text colors to LinkedIn blue rgba(0, 117, 181), excluding center logo and middle positions"""
    print("Changing icon and verb colors to LinkedIn blue...")
    
    # Convert to numpy array for pixel manipulation
    img_array = np.array(quilt)
    height, width = img_array.shape[:2]
    
    # LinkedIn blue RGB: rgba(0, 117, 181)
    linkedin_blue = np.array([0, 117, 181])
    
    # Define center region where LinkedIn logo is (middle tile)
    center_x_start = width // 3
    center_x_end = 2 * width // 3
    center_y_start = height // 3
    center_y_end = 2 * height // 3
    
    # Define middle-left and middle-right regions to exclude (completely blank)
    middle_left_x_start = 0
    middle_left_x_end = CELL_WIDTH
    middle_left_y_start = CELL_HEIGHT
    middle_left_y_end = 2 * CELL_HEIGHT
    
    middle_right_x_start = 2 * CELL_WIDTH
    middle_right_x_end = 3 * CELL_WIDTH
    middle_right_y_start = CELL_HEIGHT
    middle_right_y_end = 2 * CELL_HEIGHT
    
    # Define corner regions where icons are - exclude UPPER portion to avoid corrupting icons
    # But allow changes in LOWER portion where text labels are
    # Top-left (Like icon) - exclude top 60% where icon is, allow bottom 40% where text is
    top_left_icon_mask = np.zeros((height, width), dtype=bool)
    top_left_icon_mask[0:int(CELL_HEIGHT*0.6), 0:CELL_WIDTH] = True
    
    # Top-right (Comment icon)
    top_right_icon_mask = np.zeros((height, width), dtype=bool)
    top_right_icon_mask[0:int(CELL_HEIGHT*0.6), 2*CELL_WIDTH:3*CELL_WIDTH] = True
    
    # Bottom-left (Repost icon) - exclude top 60% where icon is
    bottom_left_icon_mask = np.zeros((height, width), dtype=bool)
    bottom_left_icon_mask[2*CELL_HEIGHT:2*CELL_HEIGHT+int(CELL_HEIGHT*0.6), 0:CELL_WIDTH] = True
    
    # Bottom-right (Send icon)
    bottom_right_icon_mask = np.zeros((height, width), dtype=bool)
    bottom_right_icon_mask[2*CELL_HEIGHT:2*CELL_HEIGHT+int(CELL_HEIGHT*0.6), 2*CELL_WIDTH:3*CELL_WIDTH] = True
    
    # Create exclusion masks
    center_mask = np.zeros((height, width), dtype=bool)
    center_mask[center_y_start:center_y_end, center_x_start:center_x_end] = True
    
    middle_left_mask = np.zeros((height, width), dtype=bool)
    middle_left_mask[middle_left_y_start:middle_left_y_end, middle_left_x_start:middle_left_x_end] = True
    
    middle_right_mask = np.zeros((height, width), dtype=bool)
    middle_right_mask[middle_right_y_start:middle_right_y_end, middle_right_x_start:middle_right_x_end] = True
    
    # Combine exclusion masks - exclude center logo, middle positions, and ALL corner cells (to protect icons)
    exclude_mask = center_mask | middle_left_mask | middle_right_mask | top_left_icon_mask | top_right_icon_mask | bottom_left_icon_mask | bottom_right_icon_mask
    
    # Target ONLY text labels (the words "Like", "Comment", "Repost", "Send")
    # These are typically below the icons, in areas between corners
    # Look for pixels that are:
    # 1. Very dark (RGB all < 50) - black text only
    # 2. Grayscale (R ≈ G ≈ B, within 3 units) - not colored content
    # 3. Not in excluded areas (corners with icons, center, middle positions)
    dark_mask = ((img_array[:, :, 0] < 50) & 
                  (img_array[:, :, 1] < 50) & 
                  (img_array[:, :, 2] < 50) &
                  ~exclude_mask)
    
    # Check if pixels are grayscale (R, G, B are very similar - within 3 units)
    r, g, b = img_array[:, :, 0].astype(float), img_array[:, :, 1].astype(float), img_array[:, :, 2].astype(float)
    is_grayscale = (np.abs(r - g) < 3) & (np.abs(g - b) < 3)
    
    # Combine: only change very dark grayscale pixels (black text labels, not icons)
    final_mask = dark_mask & is_grayscale
    
    # Replace with LinkedIn blue
    img_array[final_mask] = linkedin_blue
    
    # Convert back to PIL Image
    result = Image.fromarray(img_array.astype('uint8'))
    
    print(f"  ✓ Changed {np.sum(final_mask)} pixels to LinkedIn blue")
    return result

def create_quilt_from_existing(existing_quilt_path, new_images_dict=None, output_file=OUTPUT_FILE):
    """
    Update existing quilt by replacing specific positions with new images.
    new_images_dict: {position_index: image_path_or_url} or None to just enhance vibrancy
    """
    print(f"Updating LinkedIn quilt from existing image...")
    
    # Load existing quilt
    if os.path.exists(existing_quilt_path):
        try:
            quilt = Image.open(existing_quilt_path)
            print(f"Loaded existing quilt: {quilt.size}")
            # Verify it's not corrupted (mostly white)
            import numpy as np
            test_array = np.array(quilt)
            white_pct = np.sum(np.all(test_array > 240, axis=2)) / (test_array.shape[0] * test_array.shape[1]) * 100
            if white_pct > 85:
                print(f"⚠️  Warning: Image is {white_pct:.1f}% white - may be corrupted. Using original from Downloads.")
                # Try to load from Downloads instead
                downloads_path = os.path.expanduser('~/Downloads/linkedin-quilt.png')
                if os.path.exists(downloads_path):
                    quilt = Image.open(downloads_path)
                    print(f"Loaded fresh copy from Downloads: {quilt.size}")
        except Exception as e:
            print(f"Error loading quilt: {e}")
            # Try Downloads
            downloads_path = os.path.expanduser('~/Downloads/linkedin-quilt.png')
            if os.path.exists(downloads_path):
                quilt = Image.open(downloads_path)
                print(f"Loaded from Downloads: {quilt.size}")
            else:
                print(f"Could not load quilt image")
                return None
    else:
        # Try Downloads
        downloads_path = os.path.expanduser('~/Downloads/linkedin-quilt.png')
        if os.path.exists(downloads_path):
            quilt = Image.open(downloads_path)
            print(f"Loaded from Downloads: {quilt.size}")
        else:
            print(f"Existing quilt not found at {existing_quilt_path}")
            return None
    
    # Convert to RGB if needed
    if quilt.mode != 'RGB':
        quilt = quilt.convert('RGB')
    
    # Clear middle-left and middle-right positions (positions 3 and 5)
    # Fill them with the background color to make them blank
    print("Clearing middle-left and middle-right positions...")
    
    from PIL import ImageDraw
    import numpy as np
    draw = ImageDraw.Draw(quilt)
    
    # Get average background color from surrounding areas (top-left corner)
    bg_sample = quilt.crop((0, 0, 50, 50))
    bg_array = np.array(bg_sample)
    bg_mean = bg_array.mean(axis=(0,1))
    bg_color = tuple(int(c) for c in bg_mean)
    
    # Position 3 = middle-left (row 1, col 0)
    row_3 = 1
    col_3 = 0
    x_3 = col_3 * CELL_WIDTH
    y_3 = row_3 * CELL_HEIGHT
    # Fill with background color
    draw.rectangle([(x_3, y_3), (x_3 + CELL_WIDTH, y_3 + CELL_HEIGHT)], fill=bg_color)
    print(f"  ✓ Cleared position 3 (middle-left)")
    
    # Position 5 = middle-right (row 1, col 2)
    row_5 = 1
    col_5 = 2
    x_5 = col_5 * CELL_WIDTH
    y_5 = row_5 * CELL_HEIGHT
    # Fill with background color
    draw.rectangle([(x_5, y_5), (x_5 + CELL_WIDTH, y_5 + CELL_HEIGHT)], fill=bg_color)
    print(f"  ✓ Cleared position 5 (middle-right)")
    
    # Don't replace with graphs - user wants these positions blank
    # Removed graph replacement code
    
    # Enhance overall vibrancy (but less aggressively)
    print("Enhancing overall image vibrancy...")
    quilt = enhance_quilt_vibrancy(quilt)
    
    # Temporarily disable color replacement to prevent icon corruption
    # Will re-enable with better targeting later
    # print("Changing icon colors to LinkedIn blue...")
    # quilt = change_icon_colors_to_linkedin_blue(quilt)
    
    # Save updated quilt
    quilt.save(output_file, 'JPEG', quality=90)
    print(f"\n✅ Saved updated quilt to {output_file}")
    
    # Also save to Quilts folder
    quilts_output = os.path.join(QUILTS_DIR, 'linkedin-posts-quilt.jpg')
    os.makedirs(QUILTS_DIR, exist_ok=True)
    quilt.save(quilts_output, 'JPEG', quality=90)
    print(f"✅ Also saved to {quilts_output}")
    
    return quilt

def create_new_quilt(image_sources, output_file=OUTPUT_FILE):
    """Create a new quilt from scratch with vibrant background"""
    print(f"Creating new LinkedIn quilt with vibrant background...")
    
    quilt_width = GRID_COLUMNS * CELL_WIDTH
    quilt_height = GRID_ROWS * CELL_HEIGHT
    
    # Use vibrant background color
    quilt = Image.new('RGB', (quilt_width, quilt_height), color=VIBRANT_BG_COLOR)
    
    total_slots = GRID_COLUMNS * GRID_ROWS
    
    for idx in range(total_slots):
        row = idx // GRID_COLUMNS
        col = idx % GRID_COLUMNS
        
        x = col * CELL_WIDTH
        y = row * CELL_HEIGHT
        
        if idx < len(image_sources) and image_sources[idx]:
            print(f"[{idx+1}/{total_slots}] Processing image {idx+1}...")
            img = download_image(image_sources[idx])
        else:
            print(f"[{idx+1}/{total_slots}] Skipping slot {idx+1}...")
            continue
        
        if img:
            if img.mode != 'RGB':
                img = img.convert('RGB')
            
            # Enhance vibrancy
            img = enhance_image_vibrancy(img)
            
            # Resize and crop
            original_width, original_height = img.size
            original_aspect = original_width / original_height
            target_aspect = CELL_WIDTH / CELL_HEIGHT
            
            if original_aspect > target_aspect:
                new_height = original_height
                new_width = int(original_height * target_aspect)
                left = (original_width - new_width) // 2
                img = img.crop((left, 0, left + new_width, new_height))
            else:
                new_width = original_width
                new_height = int(original_width / target_aspect)
                top = 0
                img = img.crop((0, top, new_width, top + new_height))
            
            img = img.resize((CELL_WIDTH, CELL_HEIGHT), Image.Resampling.LANCZOS)
            quilt.paste(img, (x, y))
    
    quilt.save(output_file, 'JPEG', quality=90)
    print(f"\n✅ Saved quilt to {output_file}")
    
    return quilt

if __name__ == '__main__':
    import sys
    import glob
    
    existing_quilt = '../frontend/public/linkedin-posts-quilt.jpg'
    downloads_path = os.path.expanduser('~/Downloads')
    
    # Check for command line arguments
    if len(sys.argv) >= 3:
        graph1_path = sys.argv[1]
        graph2_path = sys.argv[2]
        print(f"Using provided graph images:")
        print(f"  Graph 1 (middle-left): {graph1_path}")
        print(f"  Graph 2 (middle-right): {graph2_path}")
        
        new_images = {
            3: graph1_path,  # middle-left: Length of tasks graph
            5: graph2_path,  # middle-right: Quality vs Effort graph
        }
        create_quilt_from_existing(existing_quilt, new_images)
    else:
        # Try to find graph images - check all recent PNG/JPG files
        all_images = glob.glob(os.path.join(downloads_path, '*.png')) + \
                     glob.glob(os.path.join(downloads_path, '*.jpg')) + \
                     glob.glob(os.path.join(downloads_path, '*.jpeg'))
        
        # Filter for recent images (last 2 days) and sort by modification time
        import time
        recent_images = []
        for img_path in all_images:
            try:
                mtime = os.path.getmtime(img_path)
                if time.time() - mtime < 172800:  # 2 days
                    recent_images.append((mtime, img_path))
            except:
                pass
        
        # Sort by modification time (newest first) and exclude the linkedin-quilt.png
        recent_images.sort(reverse=True)
        graph_candidates = [path for _, path in recent_images if 'linkedin-quilt' not in path.lower()]
        
        if len(graph_candidates) >= 2:
            graph1_path = graph_candidates[0]
            graph2_path = graph_candidates[1]
            print(f"Found recent images (using newest 2):")
            print(f"  Graph 1 (middle-left): {graph1_path}")
            print(f"  Graph 2 (middle-right): {graph2_path}")
            
            new_images = {
                3: graph1_path,  # middle-left: Length of tasks graph
                5: graph2_path,  # middle-right: Quality vs Effort graph
            }
            create_quilt_from_existing(existing_quilt, new_images)
        else:
            print("⚠️  Could not find 2 recent graph images in Downloads.")
            print("\nPlease save the two graph images to your Downloads folder, then run:")
            print("  python create_linkedin_quilt.py")
            print("\nOr provide paths directly:")
            print("  python create_linkedin_quilt.py <graph1_path> <graph2_path>")
            
            # Just enhance vibrancy if no images found
            print("\nEnhancing existing quilt vibrancy only for now...")
            create_quilt_from_existing(existing_quilt, new_images_dict=None)

