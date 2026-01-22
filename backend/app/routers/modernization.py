from fastapi import APIRouter, UploadFile, File, HTTPException, BackgroundTasks
from app.models.schemas import AnalyzeRequest, ProcessingStateResponse, ProcessingStatus
from app.services.storage import storage_service
from app.utils.sanitizer import sanitizer_service
import shutil
import os
import uuid
import zipfile
import aiofiles

router = APIRouter()

TEMP_DIR = "temp"
os.makedirs(TEMP_DIR, exist_ok=True)

@router.post("/upload", response_model=ProcessingStateResponse)
async def upload_zombie_code(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...)
):
    """
    Ingest Step:
    1. Receive ZIP
    2. Save locally
    3. Sanitize (Remove Secrets)
    4. Upload to GCS
    """
    if not file.filename.endswith('.zip'):
        raise HTTPException(status_code=400, detail="Only .zip files are supported")

    submission_id = str(uuid.uuid4())
    upload_path = os.path.join(TEMP_DIR, f"{submission_id}_{file.filename}")
    extract_path = os.path.join(TEMP_DIR, submission_id)

    # 1. Save locally
    try:
        async with aiofiles.open(upload_path, 'wb') as out_file:
            content = await file.read()
            await out_file.write(content)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to save file: {str(e)}")

    # 2. Extract and Sanitize
    try:
        with zipfile.ZipFile(upload_path, 'r') as zip_ref:
            zip_ref.extractall(extract_path)
        
        # Run Sanitizer
        sanitizer_service.sanitize_directory(extract_path)
        
        # Re-zip for GCS upload (Sanitized version)
        sanitized_zip_path = os.path.join(TEMP_DIR, f"sanitized_{submission_id}.zip")
        shutil.make_archive(sanitized_zip_path.replace('.zip', ''), 'zip', extract_path)
        
    except Exception as e:
        # cleanup
        shutil.rmtree(extract_path, ignore_errors=True)
        if os.path.exists(upload_path): os.remove(upload_path)
        raise HTTPException(status_code=500, detail=f"Processing failed: {str(e)}")

    # 3. Upload to GCS (Background Task or Direct? Direct for now to confirm receipt)
    # in a real high-scale system, we'd confirm receipt and process async. 
    # For this MVP, let's wait for GCS upload to ensure it's safe.
    try:
        gcs_uri = await storage_service.upload_file(
            sanitized_zip_path, 
            f"uploads/{submission_id}/source.zip"
        )
    except Exception as e:
         raise HTTPException(status_code=500, detail=f"GCS Upload failed: {str(e)}")

    # Cleanup temp files
    # background_tasks.add_task(cleanup_temp, submission_id) 
    # For debugging, maybe keep them? No, let's clean up.
    shutil.rmtree(extract_path, ignore_errors=True)
    os.remove(upload_path)
    os.remove(sanitized_zip_path)

    return ProcessingStateResponse(
        submission_id=submission_id,
        status=ProcessingStatus.UPLOADED,
        message="Zombie code received and sanitized. Ready for autopsyt.",
        steps_completed=["ingest", "sanitize", "storage"],
        current_step="auditing"
    )

def cleanup_temp(submission_id: str):
    # Implementation for delayed cleanup if needed
    pass
