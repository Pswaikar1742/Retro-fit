from fastapi import APIRouter, UploadFile, File, HTTPException
from typing import Dict
from app.services.build_orchestrator import BuildOrchestrator
from app.services.storage_manager import StorageManager
from app.utils.sanitizer import sanitize_code

router = APIRouter()
storage_manager = StorageManager()
build_orchestrator = BuildOrchestrator()

@router.post("/upload/")
async def upload_code(file: UploadFile = File(...)) -> Dict[str, str]:
    try:
        # Save the uploaded file to temporary storage
        file_location = f"temp/{file.filename}"
        with open(file_location, "wb") as f:
            f.write(await file.read())
        
        # Sanitize the code to remove PII and secrets
        sanitized_code = sanitize_code(file_location)
        
        # Trigger the build process
        build_result = build_orchestrator.trigger_build(sanitized_code)
        
        if build_result['status'] == 'success':
            return {"message": "Build succeeded", "url": build_result['url']}
        else:
            raise HTTPException(status_code=400, detail="Build failed")
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))