import uuid, shutil, os
from fastapi import APIRouter, UploadFile, BackgroundTasks, Depends
from app.core.security import verify_api_key
from app.services.image_converter import convert_image
from app.services.document_converter import pdf_to_docx, txt_to_docx
from app.services.audio_converter import convert_audio
from app.services.spreadsheet_converter import convert_spreadsheet
from app.services.presentation_converter import convert_presentation
from app.services.video_converter import convert_video, extract_audio_from_video
from app.services.temp_manager import save_temp
from app.core.firebase import update_job

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
            
            # Image conversions
            if file_ext in ["png", "jpg", "jpeg", "webp", "bmp", "tiff", "gif"]:
                convert_image(input_path, output_path, target_format)
            
            # Document conversions
            elif file_ext == "pdf" and target_format.lower() == "docx":
                pdf_to_docx(input_path, output_path)
            elif file_ext == "txt" and target_format.lower() == "docx":
                txt_to_docx(input_path, output_path)
            
            # Audio conversions
            elif file_ext in ["mp3", "wav", "ogg", "flac", "aac", "m4a", "wma"]:
                convert_audio(input_path, output_path, target_format)
            
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
                if target_format.lower() in ["mp4", "avi", "mov", "webm", "gif"]:
                    convert_video(input_path, output_path, target_format)
                elif target_format.lower() in ["mp3", "wav"]:
                    # Extract audio from video
                    extract_audio_from_video(input_path, output_path)
                else:
                    raise ValueError(f"Unsupported video conversion: {file_ext} -> {target_format}")
            
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
    return {
        "supported_conversions": {
            "images": {
                "input_formats": ["png", "jpg", "jpeg", "webp", "bmp", "tiff", "gif"],
                "output_formats": ["png", "jpg", "jpeg", "webp", "bmp", "tiff"]
            },
            "documents": {
                "pdf_to": ["docx"],
                "txt_to": ["docx"]
            },
            "audio": {
                "input_formats": ["mp3", "wav", "ogg", "flac", "aac", "m4a", "wma"],
                "output_formats": ["mp3", "wav", "ogg", "flac", "aac", "m4a"]
            },
            "spreadsheets": {
                "input_formats": ["csv", "xlsx", "xls"],
                "output_formats": ["csv", "xlsx", "xls", "json", "html"]
            },
            "presentations": {
                "pptx_to": ["txt", "json"],
                "txt_to": ["pptx"]
            },
            "video": {
                "input_formats": ["mp4", "avi", "mov", "webm", "mkv", "flv"],
                "output_formats": ["mp4", "avi", "mov", "webm", "gif"],
                "extract_audio_to": ["mp3", "wav"]
            }
        },
        "examples": {
            "image": "PNG to JPG, WEBP to PNG",
            "audio": "MP3 to WAV, FLAC to MP3",
            "spreadsheet": "CSV to XLSX, Excel to JSON",
            "presentation": "PPTX to TXT, TXT to PPTX",
            "video": "MP4 to GIF, AVI to MP4",
            "video_audio": "MP4 to MP3 (extract audio)"
        }
    }