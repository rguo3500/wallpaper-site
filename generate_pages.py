import os
import json

# Load data
data_js_path = '/home/ubuntu/wallpaper-site-v2/js/data.js'
with open(data_js_path, 'r') as f:
    content = f.read()
    # Simple extraction of the array from JS file
    start = content.find('const WALLPAPER_DATA = [') + len('const WALLPAPER_DATA = ')
    end = content.find('];', start) + 1
    wallpapers = json.loads(content[start:end])
    
    start_cat = content.find('const CATEGORIES = [') + len('const CATEGORIES = ')
    end_cat = content.find('];', start_cat) + 1
    categories = json.loads(content[start_cat:end_cat])

# Templates
DETAIL_TEMPLATE = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{title} | HD Mobile Wallpaper | Wallpaper Site Pro</title>
    <meta name="description" content="{description}">
    <link rel="stylesheet" href="/css/style.css">
    <script type="application/ld+json">
    {structured_data}
    </script>
</head>
<body>
    <nav>
        <div class="logo">Wallpaper Pro</div>
        <ul class="nav-links">
            <li><a href="/">Home</a></li>
            <li><a href="/category/phone.html">Phone</a></li>
            <li><a href="/category/tablet.html">Tablet</a></li>
            <li><a href="/category/dream-zodiac.html">Zodiac</a></li>
            <li><a href="/category/zodiac-constellation.html">Constellation</a></li>
            <li><a href="/category/anime.html">Anime</a></li>
        </ul>
        <button class="theme-toggle">🌓</button>
    </nav>

    <main style="padding: 40px 5%;">
        <nav class="breadcrumb" style="margin-bottom: 20px; color: var(--secondary-text);">
            <a href="/">Home</a> / <a href="/category/{category}.html">{category_name}</a> / {title}
        </nav>

        <div style="display: grid; grid-template-columns: 1fr 350px; gap: 40px;">
            <div class="preview-container">
                <img src="{image}" alt="{title}" style="width: 100%; border-radius: 18px; box-shadow: 0 20px 40px rgba(0,0,0,0.1);">
            </div>
            <div class="info-container">
                <h1 style="font-size: 2rem; margin-bottom: 20px;">{title}</h1>
                <div style="background: var(--card-bg); padding: 25px; border-radius: 18px;">
                    <p style="margin-bottom: 10px;"><strong>Resolution:</strong> {resolution}</p>
                    <p style="margin-bottom: 10px;"><strong>Device:</strong> {device}</p>
                    <p style="margin-bottom: 10px;"><strong>Category:</strong> {category_name}</p>
                    <p style="margin-bottom: 20px;"><strong>Color:</strong> {color}</p>
                    <a href="{image}" download class="download-btn" style="display: block; background: var(--primary-color); color: white; text-align: center; padding: 15px; border-radius: 30px; font-weight: 600;">Download Wallpaper</a>
                </div>
                
                <div style="margin-top: 30px;">
                    <h3>Tags</h3>
                    <div style="display: flex; flex-wrap: wrap; gap: 10px; margin-top: 10px;">
                        {tags_html}
                    </div>
                </div>
            </div>
        </div>

        <section style="margin-top: 60px;">
            <h2>FAQ</h2>
            <div style="margin-top: 20px;">
                <p><strong>How to set this wallpaper?</strong><br>Download the image, go to your phone settings, and select it as your background.</p>
            </div>
        </section>
    </main>

    <script src="/js/data.js"></script>
    <script src="/js/app.js"></script>
</body>
</html>
"""

# Generate Detail Pages
os.makedirs('/home/ubuntu/wallpaper-site-v2/wallpaper', exist_ok=True)
for wp in wallpapers:
    structured_data = {
        "@context": "https://schema.org/",
        "@type": "ImageObject",
        "name": wp['title'],
        "description": wp['description'],
        "contentUrl": wp['image'],
        "author": {"@type": "Organization", "name": "Wallpaper Site Pro"}
    }
    
    tags_html = "".join([f'<span style="background: var(--card-bg); padding: 5px 15px; border-radius: 20px; font-size: 0.9rem;">{tag}</span>' for tag in wp['tags']])
    
    html = DETAIL_TEMPLATE.format(
        title=wp['title'],
        description=wp['description'],
        image=wp['image'],
        resolution=wp['resolution'],
        device=wp['device'],
        category=wp['category'],
        category_name=wp['category'].capitalize(),
        color=wp['color'],
        tags_html=tags_html,
        structured_data=json.dumps(structured_data)
    )
    
    with open(f"/home/ubuntu/wallpaper-site-v2/wallpaper/{wp['slug']}.html", 'w') as f:
        f.write(html)

# Generate Category Pages
with open('/home/ubuntu/wallpaper-site-v2/category-template.html', 'r') as f:
    CAT_TEMPLATE = f.read()

os.makedirs('/home/ubuntu/wallpaper-site-v2/category', exist_ok=True)
for cat in categories:
    html = CAT_TEMPLATE.replace("{category_name}", cat['name'])\
                      .replace("{category_description}", cat['description'])\
                      .replace("{category_slug}", cat['slug'])\
                      .replace("{seo_text}", f"Find the best {cat['name']} wallpapers for your phone. Our {cat['name']} collection features high-definition backgrounds that are perfect for any mobile screen.")
    
    with open(f"/home/ubuntu/wallpaper-site-v2/category/{cat['slug']}.html", 'w') as f:
        f.write(html)

print(f"Generated {len(wallpapers)} detail pages and {len(categories)} category pages.")
