#!/usr/bin/env python3
"""
Wallpaper Hub V3.2 - Automatic Tag Page Generator
Generates individual SEO-optimized pages for each tag with auto-aggregation.
"""

import os
import json
import re
from pathlib import Path

# Load data
import json
import re

with open('js/data.js', 'r', encoding='utf-8') as f:
    data_content = f.read()

# Parse JavaScript arrays
def extract_js_array(content, var_name):
    pattern = rf'const {var_name} = \[(.*?)\];'
    match = re.search(pattern, content, re.DOTALL)
    if match:
        array_str = '[' + match.group(1) + ']'
        # Convert JavaScript to JSON
        array_str = array_str.replace("'", '"')
        return json.loads(array_str)
    return []

WALLPAPER_DATA = extract_js_array(data_content, 'WALLPAPER_DATA')
TAGS = extract_js_array(data_content, 'TAGS')

def generate_tag_pages():
    """Generate individual pages for each tag."""
    tag_dir = Path('tag')
    tag_dir.mkdir(exist_ok=True)
    
    # Read template
    with open('tag-template.html', 'r', encoding='utf-8') as f:
        template = f.read()
    
    # Create a mapping of tag slug to wallpapers
    tag_wallpapers = {}
    for tag in TAGS:
        tag_wallpapers[tag['slug']] = []
    
    # Aggregate wallpapers by tag
    for wallpaper in WALLPAPER_DATA:
        for tag_slug in wallpaper.get('tags', []):
            if tag_slug not in tag_wallpapers:
                tag_wallpapers[tag_slug] = []
            tag_wallpapers[tag_slug].append(wallpaper)
    
    # Update tag counts
    for tag in TAGS:
        tag['count'] = len(tag_wallpapers.get(tag['slug'], []))
    
    # Generate pages for each tag
    for tag in TAGS:
        tag_slug = tag['slug']
        tag_name = tag['name']
        tag_count = len(tag_wallpapers.get(tag_slug, []))
        
        # Generate wallpaper items HTML
        wallpaper_items = ""
        for wp in tag_wallpapers.get(tag_slug, []):
            wallpaper_items += f"""
            <div class="masonry-item">
                <a href="/wallpaper/{wp['slug']}.html">
                    <img src="{wp['image']}" alt="{wp['title']}" loading="lazy">
                    <div class="item-info">
                        <div class="item-title">{wp['title']}</div>
                        <div class="item-meta"><span>👁 {wp['views']:,}</span> <span>⭐ {wp['rating']}</span></div>
                    </div>
                </a>
            </div>
            """
        
        # Generate related tags
        related_tags = ""
        for related_tag in TAGS[:5]:  # Show top 5 related tags
            if related_tag['slug'] != tag_slug:
                related_tags += f'<a href="/tag/{related_tag["slug"]}/" class="tag-item">{related_tag["name"]}</a>\n'
        
        # Replace placeholders
        page_content = template.replace('{{TAG_NAME}}', tag_name)
        page_content = page_content.replace('{{TAG_SLUG}}', tag_slug)
        page_content = page_content.replace('{{TAG_COUNT}}', str(tag_count))
        page_content = page_content.replace('{{WALLPAPER_ITEMS}}', wallpaper_items)
        page_content = page_content.replace('{{RELATED_TAGS}}', related_tags)
        
        # Write page
        page_path = tag_dir / f'{tag_slug}.html'
        with open(page_path, 'w', encoding='utf-8') as f:
            f.write(page_content)
        
        print(f"✅ Generated: /tag/{tag_slug}/ ({tag_count} wallpapers)")
    
    # Generate tag index page
    generate_tag_index()

def generate_tag_index():
    """Generate the main tag index page."""
    tag_index = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <meta name="description" content="Browse all wallpaper tags - Anime, Cute, Pink, Blue, 4K, and more. Find your perfect wallpaper by tag.">
    <title>All Wallpaper Tags | Wallpaper Hub</title>
    <link rel="stylesheet" href="/css/style.css">
</head>
<body>
    <nav>
        <div class="logo">🎨 Wallpaper Hub</div>
        <ul class="nav-links">
            <li><a href="/">Home</a></li>
            <li><a href="/tag/">Tags</a></li>
            <li><a href="/collection/">Collections</a></li>
        </ul>
    </nav>

    <header class="hero">
        <h1>Browse All Tags</h1>
        <p>Find wallpapers by tag. Click any tag to explore related designs.</p>
    </header>

    <section class="section">
        <div style="display: grid; grid-template-columns: repeat(auto-fill, minmax(150px, 1fr)); gap: 15px;">
"""
    
    for tag in TAGS:
        count = tag.get('count', 0)
        tag_index += f"""            <a href="/tag/{tag['slug']}/" class="tag-item" style="padding: 20px; text-align: center; display: block;">
                <div style="font-size: 1.2rem; margin-bottom: 5px;">{tag['name']}</div>
                <div style="font-size: 0.85rem; color: var(--secondary-text);">{count} wallpapers</div>
            </a>
"""
    
    tag_index += """        </div>
    </section>

    <footer>
        <div class="footer-bottom">
            <p>&copy; 2024 Wallpaper Hub. All rights reserved.</p>
        </div>
    </footer>

    <script src="/js/data.js"></script>
</body>
</html>
"""
    
    with open('tag/index.html', 'w', encoding='utf-8') as f:
        f.write(tag_index)
    
    print("✅ Generated: /tag/index.html")

if __name__ == '__main__':
    print("🚀 Generating Tag Pages...")
    generate_tag_pages()
    print("\n✨ Tag page generation complete!")
