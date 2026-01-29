from fastapi import APIRouter, HTTPException
from typing import Optional
import requests
import os
import uuid
import zipfile
import logging

logger = logging.getLogger(__name__)
router = APIRouter()

TEMP_DIR = "temp"
os.makedirs(TEMP_DIR, exist_ok=True)

@router.post("/github-import")
def import_from_github(repo_url: str, branch: Optional[str] = "main"):
    """
    Import legacy code from a GitHub repository.
    """
    if not repo_url.startswith("https://github.com/"):
        raise HTTPException(status_code=400, detail="Invalid GitHub URL")

    submission_id = str(uuid.uuid4())
    zip_path = os.path.join(TEMP_DIR, f"{submission_id}.zip")
    extract_path = os.path.join(TEMP_DIR, submission_id)

    try:
        # Download repository as ZIP
        logger.info(f"[{submission_id}] Downloading repository: {repo_url} (branch: {branch})")
        zip_url = f"{repo_url}/archive/{branch}.zip"
        response = requests.get(zip_url)
        response.raise_for_status()

        with open(zip_path, "wb") as zip_file:
            zip_file.write(response.content)

        # Extract ZIP
        logger.info(f"[{submission_id}] Extracting repository ZIP")
        with zipfile.ZipFile(zip_path, "r") as zip_ref:
            zip_ref.extractall(extract_path)

        # Return success message
        return {
            "submission_id": submission_id,
            "message": "Repository imported successfully",
            "files": os.listdir(extract_path)
        }

    except Exception as e:
        logger.error(f"[{submission_id}] Failed to import repository: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to import repository: {str(e)}")

    finally:
        # Cleanup
        if os.path.exists(zip_path):
            os.remove(zip_path)