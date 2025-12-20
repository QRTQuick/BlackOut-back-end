import uuid, shutil, os
from fastapi import APIRouter, UploadFile, BackgroundTasks, Depends
from app.core.security import verify_api_key
from app.services.image_converter import convert_image
from app.services.document_converter import pdf_to_docx, txt_to_docx, docx_to_txt, docx_to_pptx
from app.services.spreadsheet_converter import convert_spreadsheet
from app.services.presentation_converter import convert_presentation
from app.services.temp_manager import save_temp
from app.core.firebase import update_job

# Optional imports for audio/video (may not be available on all platforms)
try:
    from app.services.audio_converter import convert_audio
    AUDIO_AVAILABLE = True
except ImportError:
    AUDIO_AVAILABLE = False
    print("Audio conversion not available - missing dependencies")

try:
    from app.services.video_converter import convert_video, extract_audio_from_video
    VIDEO_AVAILABLE = True
except ImportError:
    VIDEO_AVAILABLE = False
    print("Video conversion not available - missing dependencies")

router = APIRouter()

@router.post("/convert")
async def convert_file(
    background_tasks: BackgroundTasks,
    file: UploadFile,
    target_format: str,
    _: str = Depends(verify_api_key)
):
    task_id = str(uuid.uuid4())
    input_path = f"app/storage/input/{task_id}_{file.filename}"
    output_path = f"app/storage/output/{task_id}.{target_format}"
    
    with open(input_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    
    update_job(task_id, {"status": "processing"})
    
    def process():
        try:
            print(f"Processing file: {file.filename} -> {target_format}")
            print(f"Input path: {input_path}")
            print(f"Output path: {output_path}")
            
            # Ensure output directory exists
            os.makedirs(os.path.dirname(output_path), exist_ok=True)
            
            file_ext = file.filename.lower().split('.')[-1] if '.' in file.filename else ''
            
            print(f"🔍 Debug: file_ext='{file_ext}', target_format='{target_format.lower()}'")
            
            # Image conversions
            if file_ext in ["png", "jpg", "jpeg", "webp", "bmp", "tiff", "gif"]:
                print("📸 Processing as image conversion")
                convert_image(input_path, output_path, target_format)
            
            # Document conversions
            elif file_ext == "pdf" and target_format.lower() == "docx":
                print("📄 Processing PDF to DOCX")
                pdf_to_docx(input_path, output_path)
            elif file_ext == "txt" and target_format.lower() == "docx":
                print("📝 Processing TXT to DOCX")
                txt_to_docx(input_path, output_path)
            elif file_ext == "txt" and target_format.lower() == "pptx":
                print("📝 Processing TXT to PPTX")
                from app.services.document_converter import txt_to_pptx
                txt_to_pptx(input_path, output_path)
            elif file_ext == "docx" and target_format.lower() == "txt":
                print("📄 Processing DOCX to TXT")
                docx_to_txt(input_path, output_path)
            elif file_ext == "docx" and target_format.lower() == "pptx":
                print("📄 Processing DOCX to PPTX")
                docx_to_pptx(input_path, output_path)
            
            # Audio conversions
            elif file_ext in ["mp3", "wav", "ogg", "flac", "aac", "m4a", "wma"]:
                print("🎵 Processing audio conversion")
                if AUDIO_AVAILABLE:
                    convert_audio(input_path, output_path, target_format)
                else:
                    raise ValueError(f"Audio conversion not available on this server. Supported conversions: Images (PNG↔JPG↔WEBP), Documents (PDF→DOCX, TXT→DOCX/PPTX, DOCX→TXT/PPTX), Spreadsheets (CSV↔XLSX↔JSON), Presentations (PPTX↔TXT)")
            
            # Spreadsheet conversions
            elif file_ext in ["csv", "xlsx", "xls"] and target_format.lower() in ["csv", "xlsx", "xls", "json", "html"]:
                convert_spreadsheet(input_path, output_path, target_format)
            
            # Presentation conversions
            elif file_ext == "pptx" and target_format.lower() in ["txt", "json"]:
                convert_presentation(input_path, output_path, target_format)
            elif file_ext == "txt" and target_format.lower() == "pptx":
                convert_presentation(input_path, output_path, target_format)
            
            # Video conversions
            elif file_ext in ["mp4", "avi", "mov", "webm", "mkv", "flv"]:
                print("🎬 Processing video conversion")
                if VIDEO_AVAILABLE:
                    if target_format.lower() in ["mp4", "avi", "mov", "webm", "gif"]:
                        convert_video(input_path, output_path, target_format)
                    elif target_format.lower() in ["mp3", "wav"]:
                        # Extract audio from video
                        extract_audio_from_video(input_path, output_path)
                    else:
                        raise ValueError(f"Unsupported video conversion: {file_ext} -> {target_format}")
                else:
                    raise ValueError(f"Video conversion not available on this server. Supported conversions: Images (PNG↔JPG↔WEBP), Documents (PDF→DOCX, TXT→DOCX/PPTX, DOCX→TXT/PPTX), Spreadsheets (CSV↔XLSX↔JSON), Presentations (PPTX↔TXT)")
            
            else:
                raise ValueError(f"Unsupported conversion: {file_ext} -> {target_format}")
            
            # Check if output file was created
            if not os.path.exists(output_path):
                raise FileNotFoundError(f"Conversion failed - output file not created: {output_path}")
            
            print(f"Conversion successful: {output_path}")
            save_temp(task_id, output_path)
            update_job(task_id, {
                "status": "completed",
                "download_url": f"/api/download/{task_id}"
            })
            
            # Clean up input file
            try:
                os.remove(input_path)
            except:
                pass
                
        except Exception as e:
            print(f"Conversion error: {str(e)}")
            update_job(task_id, {
                "status": "failed",
                "error": str(e)
            })
            # Clean up input file on error
            try:
                os.remove(input_path)
            except:
                pass
    
    background_tasks.add_task(process)
    return {"task_id": task_id}

@router.get("/formats")
def get_supported_formats():
    """Get all supported file formats and conversions"""
    formats = {
        "supported_conversions": {
            "images": {
                "input_formats": ["png", "jpg", "jpeg", "webp", "bmp", "tiff", "gif"],
                "output_formats": ["png", "jpg", "jpeg", "webp", "bmp", "tiff"]
            },
            "documents": {
                "pdf_to": ["docx"],
                "txt_to": ["docx", "pptx"],
                "docx_to": ["txt", "pptx"]
            },
            "spreadsheets": {
                "input_formats": ["csv", "xlsx", "xls"],
                "output_formats": ["csv", "xlsx", "xls", "json", "html"]
            },
            "presentations": {
                "pptx_to": ["txt", "json"],
                "txt_to": ["pptx"]
            }
        },
        "examples": {
            "image": "PNG to JPG, WEBP to PNG",
            "document": "PDF to DOCX, TXT to PPTX, DOCX to TXT",
            "spreadsheet": "CSV to XLSX, Excel to JSON",
            "presentation": "PPTX to TXT, TXT to PPTX"
        },
        "availability": {
            "audio": AUDIO_AVAILABLE,
            "video": VIDEO_AVAILABLE
        }
    }
    
    # Add audio/video formats only if available
    if AUDIO_AVAILABLE:
        formats["supported_conversions"]["audio"] = {
            "input_formats": ["mp3", "wav", "ogg", "flac", "aac", "m4a", "wma"],
            "output_formats": ["mp3", "wav", "ogg", "flac", "aac", "m4a"]
        }
        formats["examples"]["audio"] = "MP3 to WAV, FLAC to MP3"
    else:
        formats["unavailable_conversions"] = formats.get("unavailable_conversions", {})
        formats["unavailable_conversions"]["audio"] = {
            "reason": "Missing system dependencies (ffmpeg)",
            "formats": ["mp3", "wav", "ogg", "flac", "aac", "m4a"]
        }
    
    if VIDEO_AVAILABLE:
        formats["supported_conversions"]["video"] = {
            "input_formats": ["mp4", "avi", "mov", "webm", "mkv", "flv"],
            "output_formats": ["mp4", "avi", "mov", "webm", "gif"],
            "extract_audio_to": ["mp3", "wav"]
        }
        formats["examples"]["video"] = "MP4 to GIF, AVI to MP4"
        formats["examples"]["video_audio"] = "MP4 to MP3 (extract audio)"
    else:
        formats["unavailable_conversions"] = formats.get("unavailable_conversions", {})
        formats["unavailable_conversions"]["video"] = {
            "reason": "Missing system dependencies (ffmpeg)",
            "formats": ["mp4", "avi", "mov", "webm", "mkv", "flv"]
        }
    
    return formats

@router.get("/test-docx")
def test_docx_conversion():
    """Test endpoint to verify DOCX conversion functions are working"""
    try:
        from app.services.document_converter import docx_to_txt, docx_to_pptx
        return {
            "status": "success",
            "message": "DOCX conversion functions imported successfully",
            "available_functions": ["docx_to_txt", "docx_to_pptx"]
        }
    except Exception as e:
        return {
            "status": "error", 
            "message": f"DOCX conversion import failed: {str(e)}"
        }

@router.get("/system-info")
def get_system_info():
    """Get information about available system dependencies and conversions"""
    import subprocess
    import sys
    
    system_info = {
        "python_version": sys.version,
        "available_conversions": {
            "images": True,  # Always available (Pillow)
            "documents": True,  # Always available (python-docx, pdf2docx)
            "spreadsheets": True,  # Always available (pandas, openpyxl)
            "presentations": True,  # Always available (python-pptx)
            "audio": AUDIO_AVAILABLE,
            "video": VIDEO_AVAILABLE
        },
        "system_dependencies": {}
    }
    
    # Check for ffmpeg
    try:
        result = subprocess.run(['ffmpeg', '-version'], capture_output=True, text=True, timeout=5)
        system_info["system_dependencies"]["ffmpeg"] = {
            "available": result.returncode == 0,
            "version": result.stdout.split('\n')[0] if result.returncode == 0 else None
        }
    except:
        system_info["system_dependencies"]["ffmpeg"] = {"available": False, "error": "Not found or timeout"}
    
    # Check for other tools
    for tool in ['python3', 'pip']:
        try:
            result = subprocess.run([tool, '--version'], capture_output=True, text=True, timeout=5)
            system_info["system_dependencies"][tool] = {
                "available": result.returncode == 0,
                "version": result.stdout.strip() if result.returncode == 0 else None
            }
        except:
            system_info["system_dependencies"][tool] = {"available": False, "error": "Not found"}
    
    return system_info