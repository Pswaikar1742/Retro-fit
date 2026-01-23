from pydantic_settings import BaseSettings
from pydantic import Field, field_validator
from typing import Optional

class Settings(BaseSettings):
    """
    Application Configuration using Pydantic Settings.
    Reads from environment variables or .env file.
    Supports both local development and GCP Cloud Run deployments.
    """
    # Project Identity
    PROJECT_NAME: str = "Retro-Fit"
    VERSION: str = "1.0.0"
    API_V1_STR: str = "/api/v1"

    # Google Cloud Platform Configuration
    GCP_PROJECT_ID: str = Field(
        default="retro-fit-dev-485215",
        description="Google Cloud Project ID"
    )
    GCP_REGION: str = Field(
        default="us-central1",
        description="GCP Region for Vertex AI and Cloud Run"
    )
    GCP_STORAGE_BUCKET: str = Field(
        default="retro-fit-dev-485215-uploads",
        description="GCS Bucket for storing zombie code and artifacts"
    )
    
    # Vertex AI Configuration
    VERTEX_AI_MODEL: str = Field(
        default="gemini-1.5-pro",
        description="Model to use for code analysis and refactoring"
    )
    VERTEX_AI_TEMPERATURE: float = Field(
        default=0.2,
        description="Temperature for Vertex AI generation (0.0-1.0)"
    )
    
    # Logging Configuration
    LOG_LEVEL: str = Field(
        default="INFO",
        description="Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)"
    )
    
    # Optional: For local dev with service account file
    GOOGLE_APPLICATION_CREDENTIALS: Optional[str] = None

    class Config:
        case_sensitive = True
        env_file = ".env"

    @field_validator('VERTEX_AI_TEMPERATURE')
    @classmethod
    def validate_temperature(cls, v: float) -> float:
        if not 0.0 <= v <= 1.0:
            raise ValueError('Temperature must be between 0.0 and 1.0')
        return v

    @field_validator('LOG_LEVEL')
    @classmethod
    def validate_log_level(cls, v: str) -> str:
        valid_levels = {'DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL'}
        if v.upper() not in valid_levels:
            raise ValueError(f'Log level must be one of {valid_levels}')
        return v.upper()

# Global settings instance
try:
    settings = Settings()
except Exception as e:
    print(f"Warning: Failed to load settings: {e}")
    print("Using default settings...")
    settings = Settings()
