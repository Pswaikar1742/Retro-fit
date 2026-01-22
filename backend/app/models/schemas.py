from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from enum import Enum

# --- Enums ---
class ProcessingStatus(str, Enum):
    PENDING = "pending"
    UPLOADED = "uploaded"
    AUDITING = "auditing"
    REFACTORING = "refactoring"
    VALIDATING = "validating"
    COMPLETED = "completed"
    FAILED = "failed"

# --- Request Models ---
class AnalyzeRequest(BaseModel):
    submission_id: str = Field(..., description="Unique ID of the uploaded zombie code submission")
    filename: str = Field(..., description="Original filename of the zip")

# --- Response Models ---
class HealthCheck(BaseModel):
    status: str = "ok"
    version: str

class AuditResult(BaseModel):
    original_architecture: str
    detected_issues: List[str]
    modernization_strategy: str

class RefactorResult(BaseModel):
    files_generated: List[str]
    dockerfile_content: str
    python_version: str = "3.11"

class ValidationResult(BaseModel):
    build_id: str
    status: str
    logs_url: Optional[str] = None
    deployed_url: Optional[str] = None

class ProcessingStateResponse(BaseModel):
    """Current state of a modernization job"""
    submission_id: str
    status: ProcessingStatus
    message: str
    steps_completed: List[str] = []
    current_step: str | None = None
    error: str | None = None
