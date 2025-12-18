# NodeBlack

FastAPI backend for file conversion with async processing.

## Features
- API Key authentication
- Image conversion (JPG/PNG/WEBP)
- Document conversion (PDF/DOCX/TXT)
- Async background tasks
- Firebase Realtime DB for job status
- SQLite for temporary download links
- 20MB file limit
- 10-minute temp file expiry

## Setup
1. Install dependencies: `pip install -r requirements.txt`
2. Add Firebase service account key as `firebase_key.json`
3. Update `.env` with your Firebase URL
4. Run: `uvicorn app.main:app --reload`

## API Usage
- POST `/api/convert` - Upload file with `target_format` parameter
- GET `/api/download/{task_id}` - Download converted file
- Header: `X-API-Key: blackout-secret-key`