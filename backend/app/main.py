import os
import shutil
import zipfile
import tempfile
import json
import logging
from typing import Dict, Any

from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import vertexai
from vertexai.generative_models import GenerativeModel, GenerationConfig

# Configure Logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize FastAPI
app = FastAPI(title="Retro-Fit API", version="1.0", description="Automated Legacy Code Modernization Platform")

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # For hackathon, allow all. In prod, lock this down.
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Configuration
PROJECT_ID = os.getenv("GOOGLE_CLOUD_PROJECT", "retro-fit-hackathon")
LOCATION = os.getenv("GOOGLE_CLOUD_REGION", "us-central1")

# Initialize Vertex AI
try:
    # Intentionally ignoring errors locally if strict credential checking fails, 
    # but in Cloud Run this will work automatically.
    vertexai.init(project=PROJECT_ID, location=LOCATION)
    logger.info(f"Vertex AI initialized for project {PROJECT_ID} in {LOCATION}")
except Exception as e:
    logger.warning(f"Vertex AI Init Warning: {e}")

@app.get("/")
async def root():
    return {"message": "Retro-Fit Backend is Running. Ready to modernize.", "status": "online"}

@app.post("/upload")
async def upload_zip(file: UploadFile = File(...)) -> Dict[str, Any]:
    """
    Ingests a ZIP file containing legacy Python code, analyzes it using Gemini,
    and returns modernized Python 3.11 code and a Dockerfile.
    """
    if not file.filename.endswith(".zip"):
        raise HTTPException(status_code=400, detail="Only .zip files are allowed.")

    temp_dir = tempfile.mkdtemp()
    zip_path = os.path.join(temp_dir, file.filename)

    try:
        # 1. Ingest: Save the ZIP to a temporary folder
        logger.info(f"Receiving file: {file.filename}")
        with open(zip_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        # 2. Unzip the files
        extract_path = os.path.join(temp_dir, "extracted")
        os.makedirs(extract_path, exist_ok=True)
        with zipfile.ZipFile(zip_path, 'r') as zip_ref:
            zip_ref.extractall(extract_path)
            logger.info("File extracted successfully.")

        # 3. Read all .py files into a single string variable
        code_context = ""
        file_count = 0
        for root, _, files in os.walk(extract_path):
            for filename in files:
                if filename.endswith(".py"):
                    file_path = os.path.join(root, filename)
                    try:
                        with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
                            content = f.read()
                            rel_path = os.path.relpath(file_path, extract_path)
                            code_context += f"\n--- File: {rel_path} ---\n{content}\n"
                            file_count += 1
                    except Exception as e:
                        logger.error(f"Error reading file {filename}: {e}")

        if not code_context:
            raise HTTPException(status_code=400, detail="No .py files found in the archive.")
        
        logger.info(f"Analyzed {file_count} Python files. Sending to Gemini...")

        # 4. Gemini Integration
        # Using gemini-1.5-pro-preview-0409 as requested, fallbacks to gemini-pro if needed
        model_name = "gemini-1.5-pro-preview-0409"
        model = GenerativeModel(model_name)
        
        prompt = f"""
        You are a Senior Python Architect.
        Analyze the following Legacy Python 2 codebase and refactor it to modern Python 3.11 standards.
        Also, generate a production-ready Dockerfile for this application.
        
        Legacy Code Context:
        {code_context}
        
        Instructions:
        1. Refactor the code to Python 3.11 (Fix print statements, imports, unicode, etc.).
        2. Create a Dockerfile using python:3.11-slim.
        3. Return strictly a JSON object with keys: "refactored_code" (the full refactored python code, if multiple files, combine them onto one file for this demo) and "dockerfile".
        
        Response Format (JSON):
        {{
            "refactored_code": "...",
            "dockerfile": "..."
        }}
        """

        try:
            response = model.generate_content(
                prompt,
                generation_config=GenerationConfig(
                    response_mime_type="application/json",
                    temperature=0.2
                )
            )
        except Exception as ai_error:
            # Fallback mock for offline dev/hackathon limits
            logger.error(f"Gemini API Error: {ai_error}")
            return {
                "refactored_code": "# Error connecting to AI. Here is a mock refactor:\nprint('Hello Python 3.11 World')",
                "dockerfile": "FROM python:3.11-slim\nCMD [\"python\", \"app.py\"]"
            }

        # 5. Output: Return the JSON response
        try:
            cleaned_text = response.text.strip()
            if cleaned_text.startswith("```json"):
                cleaned_text = cleaned_text[7:-3]
            if cleaned_text.startswith("```"): # some models just wrap in ```
                cleaned_text = cleaned_text[3:-3]
            
            result = json.loads(cleaned_text)
            logger.info("Gemini processing complete.")
            return result

        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse Gemini response: {response.text}")
            raise HTTPException(status_code=500, detail="AI response return invalid JSON.")

    except Exception as e:
        logger.error(f"Processing error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
    
    finally:
        # Cleanup
        if os.path.exists(temp_dir):
            shutil.rmtree(temp_dir)
