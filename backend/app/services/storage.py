import asyncio
import logging
import os
import shutil
from google.cloud import storage
from pathlib import Path
from app.core.config import settings

logger = logging.getLogger(__name__)

class StorageService:
    def __init__(self, use_mock: bool = None):
        """Initialize GCS client with project credentials or mock mode."""
        # Auto-detect mock mode if credentials not available
        if use_mock is None:
            use_mock = not os.path.exists(os.getenv('GOOGLE_APPLICATION_CREDENTIALS', ''))
        
        self.use_mock = use_mock
        self.bucket_name = settings.GCP_STORAGE_BUCKET
        self.credentials_path = os.getenv("GOOGLE_APPLICATION_CREDENTIALS")
        self.local_storage_path = Path("temp/uploads")

        if self.use_mock:
            logger.info("Using MOCK storage mode (no GCP credentials)")
            self.client = None
        else:
            try:
                self.client = storage.Client(project=settings.GCP_PROJECT_ID)
                logger.info(f"GCS initialized: project={settings.GCP_PROJECT_ID}, bucket={self.bucket_name}")
            except Exception as e:
                logger.warning(f"Failed to initialize real GCS client: {e}, falling back to mock mode")
                self.use_mock = True
                self.client = None

        if not self.use_mock and not self.credentials_path:
            self.use_mock = True
            logger.info("No Google Cloud credentials found, switching to local storage.")
        
        if self.use_mock:
            self.local_storage_path.mkdir(parents=True, exist_ok=True)

    async def upload_file(self, source_file_name: str, destination_blob_name: str) -> str:
        """
        Uploads a file to the bucket asynchronously.
        Supports both real GCS and mock mode.
        """
        if self.use_mock:
            # Mock mode - simulate upload
            logger.info(f"[MOCK] Simulating upload: {source_file_name} → gs://{self.bucket_name}/{destination_blob_name}")
            return f"gs://{self.bucket_name}/{destination_blob_name}"
        
        if not self.client:
            raise RuntimeError("GCS client not initialized")
        
        try:
            # Run blocking GCS operation in a thread pool
            loop = asyncio.get_event_loop()
            gcs_uri = await loop.run_in_executor(
                None,
                self._upload_blocking,
                source_file_name,
                destination_blob_name
            )
            logger.info(f"File uploaded: {gcs_uri}")
            return gcs_uri
        except FileNotFoundError as e:
            logger.error(f"Source file not found: {source_file_name}")
            raise ValueError(f"Source file not found: {source_file_name}") from e
        except Exception as e:
            logger.error(f"GCS upload failed: {type(e).__name__}: {e}")
            raise

    def _upload_blocking(self, source_file_name: str, destination_blob_name: str) -> str:
        """
        Blocking upload operation (runs in thread pool).
        Separated from async method for clarity.
        """
        if self.use_mock:
            return self._upload_to_local(source_file_name, destination_blob_name)

        bucket = self.client.bucket(self.bucket_name)
        blob = bucket.blob(destination_blob_name)
        blob.upload_from_filename(source_file_name)
        return f"gs://{self.bucket_name}/{destination_blob_name}"

    def _upload_to_local(self, file_path: str, destination: str):
        try:
            dest_path = self.local_storage_path / destination
            shutil.copy(file_path, dest_path)
            logger.info(f"Uploaded {file_path} to local storage at {dest_path}.")
            return str(dest_path)
        except Exception as e:
            logger.error(f"Failed to upload to local storage: {e}")
            raise

    def list_files(self, prefix: str):
        """Lists all the blobs in the bucket that begin with the prefix."""
        if not self.client:
            raise RuntimeError("GCS client not initialized")
        bucket = self.client.bucket(self.bucket_name)
        blobs = bucket.list_blobs(prefix=prefix)
        return [blob.name for blob in blobs]

storage_service = StorageService()
