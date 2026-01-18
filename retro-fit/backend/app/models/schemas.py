from pydantic import BaseModel
from typing import Optional, List

class CodeUploadSchema(BaseModel):
    file_name: str
    file_size: int
    upload_time: str

class RefactorRequestSchema(BaseModel):
    code: str
    language: str = "python"
    target_version: str = "3.11"

class RefactorResponseSchema(BaseModel):
    success: bool
    refactored_code: Optional[str] = None
    error_message: Optional[str] = None

class BuildTriggerSchema(BaseModel):
    project_id: str
    trigger_id: str
    source: str

class BuildResultSchema(BaseModel):
    build_id: str
    status: str
    logs: List[str]