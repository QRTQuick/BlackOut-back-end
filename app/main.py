from fastapi import FastAPI
from fastapi.responses import FileResponse, HTMLResponse
from fastapi.staticfiles import StaticFiles
from app.api.convert import router
from app.services.temp_manager import init_db, get_temp
from app.services.keep_alive import keep_alive_service
import time, os
import asyncio

app = FastAPI(
    title="NodeBlack API",
    description="Universal File Converter - Transform any file format with lightning speed",
    version="2.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

init_db()
app.include_router(router, prefix="/api")

# Serve static files and landing page
try:
    app.mount("/frontend", StaticFiles(directory="frontend"), name="frontend")
except:
    pass  # Frontend directory might not exist

@app.get("/", response_class=HTMLResponse)
async def landing_page():
    """Serve the developer landing page - First thing users see!"""
    # Priority order: Try to find your custom index.html first
    possible_paths = [
        "index.html",  # Root directory (highest priority)
        "../index.html",  # Parent directory
        "/opt/render/project/src/index.html",  # Render deployment path
        os.path.join(os.path.dirname(os.path.dirname(__file__)), "index.html"),  # Relative to app
        "./index.html",  # Current working directory
        os.path.join(os.getcwd(), "index.html")  # Absolute current directory
    ]
    
    print(f"🔍 Looking for index.html in these locations:")
    for i, path in enumerate(possible_paths, 1):
        print(f"  {i}. {path} - {'✅ Found' if os.path.exists(path) else '❌ Not found'}")
        try:
            if os.path.exists(path):
                print(f"📄 Serving index.html from: {path}")
                with open(path, "r", encoding="utf-8") as f:
                    return HTMLResponse(content=f.read())
        except Exception as e:
            print(f"❌ Error reading {path}: {e}")
            continue
    
    # Fallback: Return inline HTML if file not found
    return HTMLResponse(content="""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>NodeBlack API - Universal File Converter</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body {
            font-family: 'Courier New', monospace;
            background: linear-gradient(135deg, #0c0c0c 0%, #1a1a1a 100%);
            color: #00ff41;
            min-height: 100vh;
            display: flex;
            align-items: center;
            justify-content: center;
            padding: 20px;
        }
        .container {
            max-width: 800px;
            background: #1a1a1a;
            border: 2px solid #00ff41;
            border-radius: 10px;
            padding: 40px;
            box-shadow: 0 0 30px rgba(0, 255, 65, 0.3);
        }
        h1 {
            font-size: 2.5em;
            margin-bottom: 20px;
            text-shadow: 0 0 15px rgba(0, 255, 65, 0.7);
            text-align: center;
        }
        .status {
            background: #0a0a0a;
            border: 1px solid #333;
            border-radius: 8px;
            padding: 20px;
            margin: 20px 0;
        }
        .status-item {
            display: flex;
            align-items: center;
            gap: 10px;
            margin: 10px 0;
            color: #cccccc;
        }
        .dot {
            width: 10px;
            height: 10px;
            border-radius: 50%;
            background: #00ff41;
            animation: pulse 2s infinite;
        }
        @keyframes pulse {
            0%, 100% { opacity: 1; }
            50% { opacity: 0.5; }
        }
        .links {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 15px;
            margin-top: 30px;
        }
        .link-card {
            background: #0a0a0a;
            border: 1px solid #333;
            border-radius: 8px;
            padding: 20px;
            text-align: center;
            text-decoration: none;
            color: #00ff41;
            transition: all 0.3s;
        }
        .link-card:hover {
            border-color: #00ff41;
            box-shadow: 0 0 15px rgba(0, 255, 65, 0.3);
            transform: translateY(-2px);
        }
        .link-card h3 {
            margin-bottom: 10px;
        }
        .link-card p {
            color: #cccccc;
            font-size: 0.9em;
        }
        code {
            background: #0a0a0a;
            padding: 2px 6px;
            border-radius: 4px;
            color: #00ff41;
        }
    </style>
</head>
<body>
    <div class="container">
        <div style="text-align: center; margin-bottom: 30px;">
            <pre style="font-size: 14px; line-height: 1.2; font-weight: bold; margin: 0; color: #00ff41; text-shadow: 0 0 10px rgba(0, 255, 65, 0.7);">
    _   __          __     ____  __           __  
   / | / /___  ____/ /__  / __ )/ /___ ______/ /__
  /  |/ / __ \/ __  / _ \/ __  / / __ `/ ___/ //_/
 / /|  / /_/ / /_/ /  __/ /_/ / / /_/ / /__/ ,&lt;   
/_/ |_/\____/\__,_/\___/_____/_/\__,_/\___/_/|_|

            </pre>
            <h2 style="background: linear-gradient(45deg, #ff4444, #ffff44, #44ff44, #44ffff, #4488ff, #ff44ff); -webkit-background-clip: text; -webkit-text-fill-color: transparent; background-clip: text; margin: 20px 0;">
                ⚡ UNIVERSAL FILE CONVERTER API ⚡
            </h2>
        </div>
        
        <div class="status">
            <div class="status-item">
                <div class="dot"></div>
                <strong>Status:</strong> <span style="color: #00ff41;">ONLINE</span>
            </div>
            <div class="status-item">
                <strong>Server:</strong> nodeblack.onrender.com
            </div>
            <div class="status-item">
                <strong>Version:</strong> 2.0.0
            </div>
            <div class="status-item">
                <strong>Keep-Alive:</strong> <span style="color: #00ff41;">Active (5sec intervals)</span>
            </div>
        </div>
        
        <div class="links">
            <a href="/docs" class="link-card">
                <h3>📖 API Docs</h3>
                <p>Interactive Swagger UI</p>
            </a>
            
            <a href="/redoc" class="link-card">
                <h3>📚 ReDoc</h3>
                <p>Alternative documentation</p>
            </a>
            
            <a href="/api/formats" class="link-card">
                <h3>🎯 Formats</h3>
                <p>Supported conversions</p>
            </a>
            
            <a href="/api/test" class="link-card">
                <h3>✅ Health Check</h3>
                <p>API status</p>
            </a>
        </div>
        
        <div style="margin-top: 30px; padding: 20px; background: #0a0a0a; border-radius: 8px;">
            <h3 style="margin-bottom: 15px;">Quick Start</h3>
            <p style="color: #cccccc; margin-bottom: 10px;">Convert a file:</p>
            <code style="display: block; padding: 15px; overflow-x: auto;">
curl -X POST "https://nodeblack.onrender.com/api/convert?target_format=jpg" \\<br>
  -H "X-API-Key: demo-key" \\<br>
  -F "file=@image.png"
            </code>
        </div>
        
        <p style="text-align: center; margin-top: 30px; color: #666;">
            Made with ❤️ by the NodeBlack team
        </p>
    </div>
</body>
</html>
    """, status_code=200)

@app.get("/home", response_class=HTMLResponse)
async def home_redirect():
    """Alternative home route - redirects to main landing page"""
    return await landing_page()

@app.get("/landing", response_class=HTMLResponse) 
async def landing_redirect():
    """Alternative landing route - redirects to main landing page"""
    return await landing_page()

@app.on_event("startup")
async def startup_event():
    """Start keep-alive service when app starts"""
    # Set the URL to your Render deployment URL
    render_url = os.getenv("RENDER_URL", "http://127.0.0.1:8000")  # Default to localhost for development
    keep_alive_service.url = render_url
    keep_alive_service.start()

@app.on_event("shutdown")
async def shutdown_event():
    """Stop keep-alive service when app shuts down"""
    keep_alive_service.stop()

@app.get("/api/files")
def list_files():
    """Get all converted files from database"""
    import sqlite3
    conn = sqlite3.connect("temp.db")
    cur = conn.cursor()
    cur.execute("SELECT task_id, file_path, expires_at FROM temp_downloads")
    rows = cur.fetchall()
    conn.close()
    
    files = []
    current_time = int(time.time())
    
    for task_id, file_path, expires_at in rows:
        status = "expired" if current_time > expires_at else "available"
        file_exists = os.path.exists(file_path)
        
        files.append({
            "task_id": task_id,
            "file_path": file_path,
            "expires_at": expires_at,
            "status": status,
            "file_exists": file_exists,
            "download_url": f"/api/download/{task_id}" if status == "available" and file_exists else None
        })
    
    return {"files": files, "total": len(files)}

@app.get("/api/ping")
def ping_endpoint():
    """Keep-alive ping endpoint"""
    return {
        "status": "alive",
        "timestamp": int(time.time()),
        "message": "Server is awake"
    }

@app.get("/api/test")
def test_endpoint():
    """Test endpoint to verify API is working"""
    return {
        "status": "working",
        "message": "NodeBlack API is running",
        "storage_exists": {
            "input": os.path.exists("app/storage/input"),
            "output": os.path.exists("app/storage/output")
        }
    }

@app.get("/api/status/{task_id}")
def get_status(task_id: str):
    """Check the status of a conversion job"""
    row = get_temp(task_id)
    if not row:
        return {"status": "not_found", "message": "Task ID not found in database"}
    
    path, expires = row
    if time.time() > expires:
        return {"status": "expired", "message": "File has expired"}
    
    if os.path.exists(path):
        return {"status": "ready", "message": "File ready for download", "path": path}
    else:
        return {"status": "processing", "message": "File is being processed or conversion failed", "expected_path": path}

@app.get("/api/download/{task_id}")
def download(task_id: str):
    row = get_temp(task_id)
    if not row:
        return {"error": "File not found or expired"}
    
    path, expires = row
    if time.time() > expires:
        try:
            os.remove(path)
        except:
            pass
        return {"error": "File expired"}
    
    # Check if file actually exists
    if not os.path.exists(path):
        return {"error": "File not found - conversion may have failed"}
    
    # Get file extension for proper filename
    file_ext = os.path.splitext(path)[1]
    filename = f"converted_{task_id}{file_ext}"
    
    # Set proper media type based on extension
    media_type_map = {
        # Images
        '.png': 'image/png',
        '.jpg': 'image/jpeg', 
        '.jpeg': 'image/jpeg',
        '.webp': 'image/webp',
        '.bmp': 'image/bmp',
        '.tiff': 'image/tiff',
        '.gif': 'image/gif',
        # Documents
        '.docx': 'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
        '.pdf': 'application/pdf',
        '.txt': 'text/plain',
        # Audio
        '.mp3': 'audio/mpeg',
        '.wav': 'audio/wav',
        '.ogg': 'audio/ogg',
        '.flac': 'audio/flac',
        '.aac': 'audio/aac',
        '.m4a': 'audio/mp4',
        # Spreadsheets
        '.csv': 'text/csv',
        '.xlsx': 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
        '.xls': 'application/vnd.ms-excel',
        '.json': 'application/json',
        '.html': 'text/html',
        # Presentations
        '.pptx': 'application/vnd.openxmlformats-officedocument.presentationml.presentation',
        # Video
        '.mp4': 'video/mp4',
        '.avi': 'video/x-msvideo',
        '.mov': 'video/quicktime',
        '.webm': 'video/webm'
    }
    
    media_type = media_type_map.get(file_ext.lower(), 'application/octet-stream')
    
    return FileResponse(
        path=path,
        filename=filename,
        media_type=media_type,
        headers={"Content-Disposition": f"attachment; filename={filename}"}
    )