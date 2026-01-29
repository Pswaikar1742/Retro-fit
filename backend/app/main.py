import os
import shutil
import zipfile
import tempfile
import json
import logging
from typing import Dict, Any, List

from fastapi import FastAPI, UploadFile, File, HTTPException, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings
from app.routers import modernization, github_import

# Configure Logging
logging.basicConfig(level=logging.getLevelName(settings.LOG_LEVEL))
logger = logging.getLogger(__name__)

# Lazy-load AI client (supports Ollama and Vertex AI)
_ai_initialized = False
def _init_ai():
    global _ai_initialized
    if _ai_initialized:
        return
    try:
        # Check if using Ollama (local-first mode)
        ollama_model = os.getenv("OLLAMA_MODEL")
        if ollama_model:
            logger.info(f"Using Ollama local model: {ollama_model}")
            _ai_initialized = True
            return
        
        # Fall back to Vertex AI if credentials exist
        import vertexai
        from vertexai.generative_models import GenerativeModel, GenerationConfig
        vertexai.init(project=settings.GCP_PROJECT_ID, location=settings.GCP_REGION)
        _ai_initialized = True
        logger.info("Vertex AI initialized")
    except Exception as e:
        logger.warning(f"AI init: {e}. Using available mode.")
        _ai_initialized = True  # Allow startup anyway

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
app.include_router(github_import.router)

# Initialize AI on startup
@app.on_event("startup")
async def startup_event():
    _init_ai()
    logger.info("Retro-Fit Backend started successfully")

@app.get("/")
async def root():
    ollama_model = os.getenv("OLLAMA_MODEL")
    mode = "Ollama (Local)" if ollama_model else "Vertex AI (Cloud)"
    return {"message": "Retro-Fit Backend is Running. Ready to modernize.", "status": "online", "ai_mode": mode}


# WebSocket for real-time log streaming
class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)
        logger.info(f"WebSocket client connected. Total: {len(self.active_connections)}")

    def disconnect(self, websocket: WebSocket):
        if websocket in self.active_connections:
            self.active_connections.remove(websocket)
        logger.info(f"WebSocket client disconnected. Total: {len(self.active_connections)}")

    async def broadcast(self, message: str):
        for connection in self.active_connections:
            try:
                await connection.send_text(message)
            except Exception:
                pass

manager = ConnectionManager()

@app.websocket("/log-streaming")
async def websocket_endpoint(websocket: WebSocket):
    await manager.connect(websocket)
    try:
        # Send welcome message
        await websocket.send_text("[System] Connected to Retro-Fit log streaming")
        while True:
            # Keep connection alive, listen for client messages
            data = await websocket.receive_text()
            # Echo or process commands if needed
            await websocket.send_text(f"[Echo] {data}")
    except WebSocketDisconnect:
        manager.disconnect(websocket)
    except Exception as e:
        logger.error(f"WebSocket error: {e}")
        manager.disconnect(websocket)