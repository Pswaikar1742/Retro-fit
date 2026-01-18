from fastapi import FastAPI
from backend.app.api.routes import router as api_router

app = FastAPI(title="Retro-Fit API", version="1.0")

app.include_router(api_router)

@app.get("/")
async def root():
    return {"message": "Welcome to the Retro-Fit API!"}