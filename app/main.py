from fastapi import FastAPI
from fastapi.responses import FileResponse
from app.api.convert import router
from app.services.temp_manager import init_db, get_temp
import time, os

app = FastAPI(title="NodeBlack")

init_db()
app.include_router(router, prefix="/api")

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
        '.png': 'image/png',
        '.jpg': 'image/jpeg', 
        '.jpeg': 'image/jpeg',
        '.webp': 'image/webp',
        '.docx': 'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
        '.pdf': 'application/pdf'
    }
    
    media_type = media_type_map.get(file_ext.lower(), 'application/octet-stream')
    
    return FileResponse(
        path=path,
        filename=filename,
        media_type=media_type,
        headers={"Content-Disposition": f"attachment; filename={filename}"}
    )