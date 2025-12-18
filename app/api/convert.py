import uuid, shutil, os
from fastapi import APIRouter, UploadFile, BackgroundTasks, Depends
from app.core.security import verify_api_key
from app.services.image_converter import convert_image
from app.services.document_converter import pdf_to_docx, txt_to_docx
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
            
            if file.filename.lower().endswith((".png", ".jpg", ".jpeg", ".webp")):
                convert_image(input_path, output_path, target_format)
            elif file.filename.lower().endswith(".pdf"):
                pdf_to_docx(input_path, output_path)
            elif file.filename.lower().endswith(".txt"):
                txt_to_docx(input_path, output_path)
            else:
                raise ValueError(f"Unsupported file type: {file.filename}")
            
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