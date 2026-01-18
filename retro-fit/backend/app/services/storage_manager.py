from google.cloud import storage
from typing import List, Optional

class StorageManager:
    def __init__(self, bucket_name: str):
        self.client = storage.Client()
        self.bucket = self.client.bucket(bucket_name)

    def upload_file(self, file_path: str, destination_blob_name: str) -> None:
        blob = self.bucket.blob(destination_blob_name)
        blob.upload_from_filename(file_path)

    def download_file(self, source_blob_name: str, destination_file_path: str) -> None:
        blob = self.bucket.blob(source_blob_name)
        blob.download_to_filename(destination_file_path)

    def list_blobs(self, prefix: Optional[str] = None) -> List[str]:
        blobs = self.bucket.list_blobs(prefix=prefix)
        return [blob.name for blob in blobs]

    def delete_blob(self, blob_name: str) -> None:
        blob = self.bucket.blob(blob_name)
        blob.delete()