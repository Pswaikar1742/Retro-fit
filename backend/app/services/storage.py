from google.cloud import storage
from app.core.config import settings
import os

class StorageService:
    def __init__(self):
        # In a real app, this client would be initialized once or efficiently managed
        # If GOOGLE_APPLICATION_CREDENTIALS is set, it picks it up automatically
        self.client = storage.Client(project=settings.GCP_PROJECT_ID)
        self.bucket_name = settings.GCP_STORAGE_BUCKET

    async def upload_file(self, source_file_name: str, destination_blob_name: str) -> str:
        """Uploads a file to the bucket."""
        try:
            bucket = self.client.bucket(self.bucket_name)
            blob = bucket.blob(destination_blob_name)

            # Uploading from local file path
            blob.upload_from_filename(source_file_name)

            print(f"File {source_file_name} uploaded to {destination_blob_name}.")
            return f"gs://{self.bucket_name}/{destination_blob_name}"
        except Exception as e:
            print(f"Failed to upload to GCS: {e}")
            raise e

    def list_files(self, prefix: str):
        """Lists all the blobs in the bucket that begin with the prefix."""
        bucket = self.client.bucket(self.bucket_name)
        blobs = bucket.list_blobs(prefix=prefix)
        return [blob.name for blob in blobs]

storage_service = StorageService()
