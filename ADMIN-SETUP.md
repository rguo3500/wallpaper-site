# Wallpaper Site Pro V2 - Admin Panel Setup Guide

## Overview

The Admin Panel allows you to upload wallpapers directly through a web interface without touching code. The backend server handles:

- Image upload and validation
- Automatic conversion to WebP format
- Data entry creation
- Automatic page generation
- Real-time progress feedback

## Prerequisites

### 1. Install Python Dependencies

```bash
pip install Flask Pillow
```

### 2. Project Structure

Your project should have:
```
wallpaper-site-v2/
├── admin.html          # Admin panel (frontend)
├── server.py           # Backend server
├── js/data.js          # Data file
├── generate_pages.py   # Page generator
├── assets/images/      # Image storage
└── ...
```

## Running the Server

### Local Development

1. Open terminal in the project directory
2. Run the server:

```bash
python server.py
```

You should see:
```
Starting Wallpaper Site Pro V2 Backend Server...
Access admin panel at: http://localhost:5000/admin.html
```

3. Open your browser and go to: **http://localhost:5000/admin.html**

### Production Deployment

For production, use a production WSGI server:

#### Option 1: Using Gunicorn

```bash
pip install gunicorn
gunicorn -w 4 -b 0.0.0.0:5000 server:app
```

#### Option 2: Using Waitress

```bash
pip install waitress
waitress-serve --port=5000 server:app
```

#### Option 3: Using Docker

Create a `Dockerfile`:

```dockerfile
FROM python:3.9-slim
WORKDIR /app
COPY . .
RUN pip install Flask Pillow
EXPOSE 5000
CMD ["python", "server.py"]
```

Build and run:
```bash
docker build -t wallpaper-site .
docker run -p 5000:5000 wallpaper-site
```

## Using the Admin Panel

### Step 1: Access Admin Panel

Navigate to: `http://your-domain.com/admin.html`

### Step 2: Upload Image

1. Click "📁 Click to select or drag & drop" or drag an image into the box
2. Supported formats: JPG, PNG
3. Maximum file size: 10MB
4. Image preview will appear

### Step 3: Fill in Details

- **Title**: Wallpaper name (e.g., "Beautiful Sunset")
- **Category**: Choose from:
  - Phone
  - Tablet
  - Anime
  - Girls
  - Mood
  - Dream Zodiac
  - Zodiac Constellation
- **Tags**: Comma-separated keywords (e.g., "sunset, nature, red")
- **Description**: Optional detailed description for SEO

### Step 4: Submit

Click "🚀 Upload & Generate" and wait for the process to complete.

The server will:
1. Validate the image
2. Convert to WebP format
3. Update `js/data.js`
4. Generate new HTML pages
5. Show success message with the new page URL

## API Endpoints

### POST /api/upload

Upload and process a new wallpaper.

**Request:**
```
Content-Type: multipart/form-data

Parameters:
- image: File (JPG/PNG)
- title: String
- category: String (phone|tablet|anime|girl|mood|dream-zodiac|zodiac-constellation)
- tags: String (comma-separated)
- description: String (optional)
```

**Response:**
```json
{
  "success": true,
  "message": "Wallpaper uploaded successfully!",
  "slug": "beautiful-sunset",
  "image": "/assets/images/phone/beautiful-sunset.webp",
  "page": "/wallpaper/beautiful-sunset.html"
}
```

### GET /api/categories

Get available categories.

**Response:**
```json
[
  {"slug": "phone", "name": "Phone"},
  {"slug": "tablet", "name": "Tablet"},
  ...
]
```

## Troubleshooting

### Server won't start

**Error**: `Address already in use`
- Solution: Change port in `server.py` or kill the process using port 5000

**Error**: `ModuleNotFoundError: No module named 'flask'`
- Solution: Run `pip install Flask`

### Upload fails

**Error**: `Invalid file type`
- Solution: Use JPG or PNG format only

**Error**: `File too large`
- Solution: Compress image or increase `MAX_FILE_SIZE` in `server.py`

**Error**: `Failed to convert image`
- Solution: Ensure Pillow is installed: `pip install Pillow`

### Pages not generating

**Error**: `Failed to generate pages`
- Solution: Check that `generate_pages.py` is in the project root
- Verify `js/data.js` exists and is readable

## Security Considerations

### For Production:

1. **Add Authentication**

Add a simple password check to `server.py`:

```python
from functools import wraps

ADMIN_PASSWORD = 'your-secure-password'

def require_auth(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        auth = request.authorization
        if not auth or auth.password != ADMIN_PASSWORD:
            return jsonify({'error': 'Unauthorized'}), 401
        return f(*args, **kwargs)
    return decorated

@app.route('/api/upload', methods=['POST'])
@require_auth
def upload_wallpaper():
    ...
```

2. **Use HTTPS**

Configure SSL/TLS on your web server (Nginx, Apache, etc.)

3. **Rate Limiting**

Add rate limiting to prevent abuse:

```bash
pip install Flask-Limiter
```

4. **Input Validation**

The current implementation validates:
- File type (JPG/PNG only)
- File size (max 10MB)
- Filename sanitization
- Category whitelist

## Performance Tips

### Image Optimization

The server automatically converts to WebP with quality 80. Adjust in `server.py`:

```python
convert_to_webp(temp_path, webp_path, quality=75)  # Lower = smaller file
```

### Batch Upload

For uploading many images at once:

1. Use the command-line tool: `python upload_tool.py`
2. Or create a batch upload script

### Caching

After upload, clear any CDN/browser caches:

```bash
# Add cache-busting headers to your web server config
```

## Monitoring

### Logs

Server logs are printed to console. For production, redirect to file:

```bash
python server.py > server.log 2>&1 &
```

### Check Uploads

View recent uploads in `assets/images/`:

```bash
ls -lh assets/images/phone/
```

## Advanced Configuration

### Change Upload Directory

Edit `server.py`:

```python
UPLOAD_FOLDER = 'custom/path/images'
```

### Change Server Port

Edit `server.py`:

```python
app.run(host='0.0.0.0', port=8000, debug=True)
```

### Disable Debug Mode

For production:

```python
app.run(host='0.0.0.0', port=5000, debug=False)
```

## Backup & Maintenance

### Regular Backups

```bash
# Backup images and data
tar -czf backup-$(date +%Y%m%d).tar.gz assets/images/ js/data.js
```

### Clean Up Old Uploads

```bash
# Remove images older than 30 days
find assets/images -type f -mtime +30 -delete
```

## Support

For issues or questions:
1. Check the troubleshooting section above
2. Review server logs for error messages
3. Verify all dependencies are installed
4. Ensure file permissions are correct (755 for directories, 644 for files)

---

**Last Updated**: July 2024
**Version**: 2.0
