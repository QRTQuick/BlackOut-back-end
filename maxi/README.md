# NodeBlack Backend Tester

PySide6 GUI application to test the NodeBlack FastAPI backend in real-time.

## Features
- ✅ Connection testing
- 📁 File selection and upload
- 🔄 Real-time conversion with progress tracking
- 📋 List all converted files from database
- ⬇️ Download converted files
- 📝 Real-time logging

## Setup
1. Install dependencies: `pip install -r requirements.txt`
2. Make sure NodeBlack backend is running on `http://127.0.0.1:8000`
3. Run: `python main.py`

## Usage
1. **Test Connection** - Verify backend is running
2. **Select File** - Choose image (PNG/JPG/WEBP) or document (PDF/TXT)
3. **Choose Format** - Select target conversion format
4. **Convert** - Start conversion process
5. **View Files** - See all converted files in database
6. **Download** - Double-click or select file to download

## Supported Conversions
- **Images**: PNG ↔ JPG ↔ WEBP
- **Documents**: PDF → DOCX, TXT → DOCX