from pydantic import BaseSettings

class Settings(BaseSettings):
    # Define your environment variables here
    google_cloud_project: str
    google_cloud_region: str
    google_cloud_storage_bucket: str
    google_cloud_build_trigger: str
    ai_engine_endpoint: str
    ai_engine_api_key: str

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"

settings = Settings()