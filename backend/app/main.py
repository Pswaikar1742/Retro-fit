import os
import shutil
import zipfile
import tempfile
import json
import logging
from typing import Dict, Any

from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings
from app.routers import modernization

# Configure Logging
logging.basicConfig(level=logging.getLevelName(settings.LOG_LEVEL))
logger = logging.getLogger(__name__)

# Lazy-load Vertex AI (can hang on import)
_vertex_ai_initialized = False
def _init_vertex_ai():
    global _vertex_ai_initialized
    if _vertex_ai_initialized:
        return
    try:
        import vertexai
        from vertexai.generative_models import GenerativeModel, GenerationConfig
        vertexai.init(project=settings.GCP_PROJECT_ID, location=settings.GCP_REGION)
        _vertex_ai_initialized = True
        logger.info("Vertex AI initialized")
    except Exception as e:
        logger.warning(f"Vertex AI init failed: {e}")
        _vertex_ai_initialized = False

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

# Include routers
app.include_router(modernization.router)

# Initialize Vertex AI
try:
    vertexai.init(project=settings.GCP_PROJECT_ID, location=settings.GCP_REGION)
    logger.info(f"Vertex AI initialized for project {settings.GCP_PROJECT_ID} in {settings.GCP_REGION}")
except Exception as e:
    logger.warning(f"Vertex AI Init Warning: {e}")

@app.get("/")
async def root():
    return {"message": "Retro-Fit Backend is Running. Ready to modernize.", "status": "online"}
