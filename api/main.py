"""
FastAPI Application — AI Fabric & Material Advisor
Main entry point for the web application.
"""

import sys
import os

# Add project root to sys.path
PROJECT_ROOT = os.path.dirname(os.path.dirname(__file__))
sys.path.insert(0, PROJECT_ROOT)

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse

from api.routes.recommend import router as recommend_router
from api.routes.chat import router as chat_router
from api.schemas.models import HealthResponse
from api.services.recommendation_service import get_recommendation_service
from api.services.chat_service import get_chat_service

# Initialize FastAPI app
app = FastAPI(
    title="AI Fabric & Material Advisor",
    description="Intelligent fabric recommendation system powered by ML and Generative AI",
    version="1.0.0",
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API routes
app.include_router(recommend_router, prefix="/api", tags=["Recommendations"])
app.include_router(chat_router, prefix="/api", tags=["Chat"])

# Serve static frontend files
frontend_dir = os.path.join(PROJECT_ROOT, "frontend")
if os.path.exists(frontend_dir):
    app.mount("/static", StaticFiles(directory=frontend_dir), name="static")


@app.get("/", include_in_schema=False)
async def serve_frontend():
    """Serve the main frontend page."""
    index_path = os.path.join(frontend_dir, "index.html")
    if os.path.exists(index_path):
        return FileResponse(index_path)
    return {"message": "AI Fabric Advisor API is running. Visit /docs for API documentation."}


@app.get("/api/health", response_model=HealthResponse, tags=["System"])
async def health_check():
    """Check system health status."""
    rec_service = get_recommendation_service()
    chat_service = get_chat_service()

    return HealthResponse(
        status="healthy",
        model_loaded=rec_service.is_model_loaded,
        dataset_loaded=rec_service.is_dataset_loaded,
        gemini_available=chat_service.is_available,
    )


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("api.main:app", host="0.0.0.0", port=8000, reload=True)
