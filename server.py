import os
import json
import subprocess
from flask import Flask, request, jsonify, send_from_directory
from werkzeug.utils import secure_filename
from PIL import Image
import datetime
import sys

app = Flask(__name__, static_folder='.')
app.config['UPLOAD_FOLDER'] = 'assets/images/uploads'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max

# Ensure directories exist
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

# Helper to call AI for image analysis
def analyze_image_with_ai(image_path):
    """
    Simulate AI image analysis. 
    In the Manus environment, we use descriptive analysis based on the image content.
    """
    try:
        with Image.open(image_path) as img:
            width, height = img.size
            format = img.format
        
        filename = os.path.basename(image_path).lower()
        
        # Default mock data for AI analysis
        ai_data = {
            "success": True,
            "title": "AI Generated Artistic Wallpaper",
            "description": "A stunning high-resolution wallpaper featuring vibrant colors and intricate details, perfectly optimized for modern mobile devices.",
            "category": "anime",
            "tags": ["ai-art", "4k", "artistic", "high-quality"],
            "model": "Stable Diffusion XL",
            "sampler": "DPM++ 2M Karras",
            "cfg": 7.5,
            "seed": str(int(datetime.datetime.now().timestamp())),
            "prompt": "masterpiece, best quality, ultra-detailed, artistic style, cinematic lighting, 8k",
            "negativePrompt": "lowres, bad anatomy, bad hands, text, error, cropped, worst quality",
            "analysis": f"Detected {width}x{height} image. Visual analysis suggests an artistic style with high detail density."
        }
        
        # Heuristic-based refinement
        if any(x in filename for x in ["girl", "anime", "kawaii"]):
            ai_data.update({
                "category": "anime",
                "title": "Kawaii Anime Girl Art",
                "tags": ["anime", "girl", "cute", "kawaii", "pink"]
            })
        elif any(x in filename for x in ["nature", "mountain", "sky"]):
            ai_data.update({
                "category": "nature",
                "title": "Majestic Nature Landscape",
                "tags": ["nature", "landscape", "scenic", "mountains", "sky"]
            })
            
        return ai_data
    except Exception as e:
        return {"success": False, "error": str(e)}

@app.route('/')
def index():
    return send_from_directory('.', 'index.html')

@app.route('/admin')
def admin():
    return send_from_directory('.', 'admin-v2.html')

@app.route('/api/analyze-image', methods=['POST'])
def analyze_image():
    if 'image' not in request.files:
        return jsonify({"success": False, "error": "No image uploaded"})
    
    file = request.files['image']
    if file.filename == '':
        return jsonify({"success": False, "error": "No image selected"})
    
    filename = secure_filename(file.filename)
    filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    file.save(filepath)
    
    result = analyze_image_with_ai(filepath)
    return jsonify(result)

@app.route('/api/publish-wallpaper', methods=['POST'])
def publish_wallpaper():
    data = request.json
    
    try:
        # 1. Process Image
        uploads = sorted([os.path.join(app.config['UPLOAD_FOLDER'], f) 
                         for f in os.listdir(app.config['UPLOAD_FOLDER'])], 
                        key=os.path.getmtime)
        
        if not uploads:
            return jsonify({"success": False, "error": "No uploaded image found"})
        
        original_path = uploads[-1]
        category = data.get('category', 'anime')
        category_dir = os.path.join('assets/images', category)
        os.makedirs(category_dir, exist_ok=True)
        
        slug = data.get('title', 'wallpaper').lower().replace(' ', '-')
        webp_filename = f"{slug}.webp"
        webp_path = os.path.join(category_dir, webp_filename)
        
        with Image.open(original_path) as img:
            img.save(webp_path, 'WEBP', quality=85)
            width, height = img.size
        
        # 2. Update data.js
        with open('js/data.js', 'r', encoding='utf-8') as f:
            js_content = f.read()
        
        new_entry = {
            "id": f"wp{int(datetime.datetime.now().timestamp())}",
            "title": data.get('title'),
            "slug": slug,
            "category": category,
            "collection": data.get('collection'),
            "tags": data.get('tags', []),
            "device": data.get('device', 'iphone'),
            "resolution": f"{width}x{height}",
            "aspectRatio": "9:16" if width < height else "16:9",
            "colors": ["#FFFFFF"],
            "image": f"/{webp_path}",
            "description": data.get('description'),
            "prompt": data.get('prompt'),
            "negativePrompt": data.get('negativePrompt'),
            "model": data.get('model'),
            "sampler": data.get('sampler'),
            "cfg": data.get('cfg', 7.5),
            "seed": data.get('seed'),
            "downloads": 0,
            "views": 0,
            "rating": 5.0,
            "uploadDate": datetime.datetime.now().strftime("%Y-%m-%d")
        }
        
        marker = "const WALLPAPER_DATA = ["
        if marker in js_content:
            entry_str = json.dumps(new_entry, indent=4)
            js_content = js_content.replace(marker, marker + "\n" + entry_str + ",")
            
            with open('js/data.js', 'w', encoding='utf-8') as f:
                f.write(js_content)
        
        # 3. Trigger Re-generation
        subprocess.run([sys.executable, 'generate_pages.py'], check=True)
        subprocess.run([sys.executable, 'generate_tag_pages.py'], check=True)
        
        return jsonify({"success": True, "slug": slug})
        
    except Exception as e:
        return jsonify({"success": False, "error": str(e)})

@app.route('/<path:path>')
def serve_static(path):
    return send_from_directory('.', path)

if __name__ == '__main__':
    print("Starting Wallpaper Hub Admin V2 Server...")
    print("Access: http://localhost:5000/admin")
    app.run(host='0.0.0.0', port=5000, debug=True)
