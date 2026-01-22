from pydantic_settings import BaseSettings
from pydantic import Field

class Settings(BaseSettings):
    """
    Application Configuration using Pydantic Settings.
    Reads from environment variables or .env file.
    """
    # Project Identity
    PROJECT_NAME: str = "Retro-Fit"
    VERSION: str = "1.0.0"
    API_V1_STR: str = "/api/v1"

    # Google Cloud Platform (Required)
    GCP_PROJECT_ID: str = Field(..., description="Google Cloud Project ID")
    GCP_REGION: str = Field("us-central1", description="GCP Region for Vertex AI and Cloud Run")
    GCP_STORAGE_BUCKET: str = Field(..., description="GCS Bucket for storing zombie code and artifacts")
    
    # Optional: For local dev with service account file
    GOOGLE_APPLICATION_CREDENTIALS: str | None = None

    class Config:
        case_sensitive = True
        env_file = ".env"

# Global settings instance
settings = Settings()
