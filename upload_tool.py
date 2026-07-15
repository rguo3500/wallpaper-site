import os
import json
import datetime
from PIL import Image

# --- Configuration ---
DATA_JS_PATH = 'js/data.js'
IMAGES_DIR = 'assets/images'
GENERATE_SCRIPT = 'generate_pages.py'

def convert_to_webp(source_path, target_path, quality=80):
    """Convert image to webp format."""
    try:
        with Image.open(source_path) as img:
            img.save(target_path, 'WEBP', quality=quality)
        return True
    except Exception as e:
        print(f"Error converting image: {e}")
        return False

def update_data_js(new_entry):
    """Append new wallpaper entry to data.js."""
    try:
        with open(DATA_JS_PATH, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Find the end of WALLPAPER_DATA array
        marker = 'const WALLPAPER_DATA = ['
        start_idx = content.find(marker)
        if start_idx == -1:
            print("Could not find WALLPAPER_DATA in data.js")
            return False
        
        # Find the closing bracket of the array
        # This is a simple approach assuming the array ends with ];
        end_idx = content.find('];', start_idx)
        
        array_content = content[start_idx + len(marker) : end_idx].strip()
        
        # Create the new entry string
        new_entry_str = json.dumps(new_entry, indent=4, ensure_ascii=False)
        
        # Construct the new content
        if array_content:
            # If array is not empty, add a comma before the new entry
            updated_array = array_content + ",\n    " + new_entry_str
        else:
            updated_array = "\n    " + new_entry_str
            
        new_content = content[:start_idx + len(marker)] + updated_array + content[end_idx:]
        
        with open(DATA_JS_PATH, 'w', encoding='utf-8') as f:
            f.write(new_content)
        return True
    except Exception as e:
        print(f"Error updating data.js: {e}")
        return False

def main():
    print("=== Wallpaper Site Pro V2 - Upload Tool ===")
    
    # 1. Get image info
    img_path = input("Enter the path to your image (JPG/PNG): ").strip('"').strip("'")
    if not os.path.exists(img_path):
        print("File not found!")
        return

    title = input("Enter wallpaper title (e.g. Beautiful Sunset): ")
    category = input("Enter category (phone/tablet/anime/girl/mood/dream-zodiac): ").lower()
    tags_input = input("Enter tags (comma separated, e.g. nature, sun, red): ")
    tags = [t.strip() for t in tags_input.split(',')]
    
    # 2. Prepare paths
    filename = os.path.basename(img_path)
    slug = filename.split('.')[0].lower().replace(' ', '-')
    webp_filename = f"{slug}.webp"
    
    target_dir = os.path.join(IMAGES_DIR, category)
    os.makedirs(target_dir, exist_ok=True)
    target_path = os.path.join(target_dir, webp_filename)
    
    # 3. Convert image
    print(f"Converting {filename} to WebP...")
    if convert_to_webp(img_path, target_path):
        print(f"Success! Image saved to {target_path}")
    else:
        return

    # 4. Create data entry
    # Get image dimensions
    with Image.open(target_path) as img:
        width, height = img.size
        resolution = f"{width}x{height}"

    new_entry = {
        "id": f"up{datetime.datetime.now().strftime('%m%d%H%M%S')}",
        "title": title,
        "slug": slug,
        "category": category,
        "collection": "general",
        "tags": tags,
        "device": "phone" if width < height else "tablet",
        "resolution": resolution,
        "color": "auto",
        "image": f"/{target_dir}/{webp_filename}",
        "description": f"High quality {title} wallpaper for mobile and tablet.",
        "downloads": 0,
        "rating": 5.0,
        "uploadDate": datetime.datetime.now().strftime("%Y-%m-%d")
    }

    # 5. Update data.js
    print("Updating data.js...")
    if update_data_js(new_entry):
        print("data.js updated successfully!")
    else:
        return

    # 6. Run generation script
    print("Generating pages...")
    os.system(f"python3 {GENERATE_SCRIPT}")
    print("All pages generated successfully!")
    
    print("\n=== Done! ===")
    print(f"1. New image: {target_path}")
    print(f"2. New page: wallpaper/{slug}.html")
    print("Next step: Upload these files to your server.")

if __name__ == "__main__":
    main()
