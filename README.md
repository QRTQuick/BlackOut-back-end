# NodeBlack API - Universal File Converter

🚀 **Transform any file format with lightning speed** - Support for 50+ file formats including images, audio, video, documents, and spreadsheets.

## 🌐 Live API
- **Base URL:** `https://nodeblack.onrender.com`
- **Documentation:** `https://nodeblack.onrender.com/docs`
- **Landing Page:** `https://nodeblack.onrender.com`

## 🔑 Quick Start

### 1. Get API Access
```bash
# Demo API Key (limited usage)
X-API-Key: demo-key

# For production, contact us for your API key
```

### 2. Convert Your First File
```bash
curl -X POST "https://nodeblack.onrender.com/api/convert?target_format=jpg" \
  -H "X-API-Key: demo-key" \
  -F "file=@your-image.png"
```

### 3. Download Result
```bash
curl -O "https://nodeblack.onrender.com/api/download/your-task-id"
```

## 📚 SDKs & Libraries

### Python
```python
from nodeblack_sdk import NodeBlackClient

client = NodeBlackClient("your-api-key")
result = client.convert_file("image.png", "jpg")
client.download_file(result["task_id"], "converted.jpg")
```

### JavaScript/Node.js
```javascript
const NodeBlackClient = require('nodeblack-sdk');

const client = new NodeBlackClient('your-api-key');
const result = await client.convertFile('image.png', 'jpg');
await client.downloadFile(result.task_id, 'converted.jpg');
```

### cURL (Any Language)
```bash
# 1. Upload & Convert
TASK_ID=$(curl -X POST "https://nodeblack.onrender.com/api/convert?target_format=mp3" \
  -H "X-API-Key: your-key" \
  -F "file=@audio.wav" | jq -r '.task_id')

# 2. Check Status
curl "https://nodeblack.onrender.com/api/status/$TASK_ID"

# 3. Download
curl -O "https://nodeblack.onrender.com/api/download/$TASK_ID"
```

## 🎯 Supported Conversions

| Category | Input Formats | Output Formats |
|----------|---------------|----------------|
| **Images** | PNG, JPG, JPEG, WEBP, BMP, TIFF, GIF | PNG, JPG, JPEG, WEBP, BMP, TIFF |
| **Audio** | MP3, WAV, OGG, FLAC, AAC, M4A | MP3, WAV, OGG, FLAC, AAC, M4A |
| **Video** | MP4, AVI, MOV, WEBM, MKV, FLV | MP4, AVI, MOV, WEBM, GIF |
| **Documents** | PDF, TXT | DOCX, TXT, PPTX |
| **Spreadsheets** | CSV, XLSX, XLS | CSV, XLSX, XLS, JSON, HTML |
| **Presentations** | PPTX, TXT | PPTX, TXT, JSON |

## 🔧 API Endpoints

### Core Endpoints
- `POST /api/convert` - Convert files
- `GET /api/download/{task_id}` - Download converted files
- `GET /api/status/{task_id}` - Check conversion status
- `GET /api/files` - List all files
- `GET /api/formats` - Get supported formats

### Utility Endpoints
- `GET /api/test` - Health check
- `GET /api/ping` - Keep-alive
- `GET /docs` - Interactive API documentation

## 💡 Usage Examples

### Batch Processing (Python)
```python
import os
from nodeblack_sdk import NodeBlackClient

client = NodeBlackClient("your-api-key")

# Convert all images in a folder
for filename in os.listdir("input/"):
    if filename.endswith(('.png', '.jpg', '.jpeg')):
        result = client.convert_file(f"input/{filename}", "webp")
        client.download_file(result["task_id"], f"output/{filename}.webp")
        print(f"✅ Converted {filename}")
```

### Audio Extraction (JavaScript)
```javascript
const client = new NodeBlackClient('your-api-key');

// Extract audio from video
const result = await client.convertFile('video.mp4', 'mp3');
await client.downloadFile(result.task_id, 'extracted-audio.mp3');
console.log('🎵 Audio extracted successfully!');
```

### Document Processing (cURL)
```bash
# Convert PDF to DOCX
curl -X POST "https://nodeblack.onrender.com/api/convert?target_format=docx" \
  -H "X-API-Key: your-key" \
  -F "file=@document.pdf"
```

## 🚦 Rate Limits & Pricing

| Plan | Rate Limit | File Size | Features |
|------|------------|-----------|----------|
| **Demo** | 10/hour | 5MB | All formats |
| **Developer** | 100/hour | 20MB | All formats + Priority |
| **Premium** | 1000/hour | 100MB | All formats + Priority + Support |

## 🛠️ Integration Examples

### React/Frontend
```javascript
const convertFile = async (file, targetFormat) => {
  const formData = new FormData();
  formData.append('file', file);
  
  const response = await fetch(`https://nodeblack.onrender.com/api/convert?target_format=${targetFormat}`, {
    method: 'POST',
    headers: { 'X-API-Key': 'your-key' },
    body: formData
  });
  
  return response.json();
};
```

### PHP
```php
<?php
$curl = curl_init();
curl_setopt_array($curl, [
    CURLOPT_URL => "https://nodeblack.onrender.com/api/convert?target_format=jpg",
    CURLOPT_POST => true,
    CURLOPT_POSTFIELDS => ['file' => new CURLFile('image.png')],
    CURLOPT_HTTPHEADER => ['X-API-Key: your-key'],
    CURLOPT_RETURNTRANSFER => true
]);
$response = curl_exec($curl);
curl_close($curl);
?>
```

### Go
```go
package main

import (
    "bytes"
    "io"
    "mime/multipart"
    "net/http"
    "os"
)

func convertFile(filePath, targetFormat, apiKey string) error {
    file, _ := os.Open(filePath)
    defer file.Close()
    
    body := &bytes.Buffer{}
    writer := multipart.NewWriter(body)
    part, _ := writer.CreateFormFile("file", filePath)
    io.Copy(part, file)
    writer.Close()
    
    req, _ := http.NewRequest("POST", 
        "https://nodeblack.onrender.com/api/convert?target_format="+targetFormat, body)
    req.Header.Set("X-API-Key", apiKey)
    req.Header.Set("Content-Type", writer.FormDataContentType())
    
    client := &http.Client{}
    resp, err := client.Do(req)
    return err
}
```

## 🔒 Security & Best Practices

### API Key Security
```bash
# ✅ Good - Use environment variables
export NODEBLACK_API_KEY="your-key"

# ❌ Bad - Don't hardcode in source
api_key = "your-key"  # Never do this!
```

### Error Handling
```python
try:
    result = client.convert_file("image.png", "jpg")
except FileNotFoundError:
    print("❌ Input file not found")
except TimeoutError:
    print("❌ Conversion timeout")
except Exception as e:
    print(f"❌ Error: {e}")
```

## 📞 Support & Community

- 📧 **Email:** support@nodeblack.com
- 💬 **Discord:** [Join our community](https://discord.gg/nodeblack)
- 🐛 **Issues:** [GitHub Issues](https://github.com/nodeblack/api/issues)
- 📖 **Docs:** [Full Documentation](https://nodeblack.onrender.com/docs)

## 🚀 Get Started Now

1. **Try the demo:** Use `demo-key` for testing
2. **Get your API key:** Contact us for production access
3. **Download SDKs:** Use our Python/JavaScript libraries
4. **Join community:** Get help and share feedback

---

**Made with ❤️ by the NodeBlack team** | [Website](https://nodeblack.onrender.com) | [API Docs](https://nodeblack.onrender.com/docs)