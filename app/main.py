"""
Main application file for the Appraisal AI Agent.
"""
import uvicorn
from fastapi import FastAPI, APIRouter
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
import os
import logging

from app.core.config import settings
from app.api.v1.api import api_router
from app.api.direct import router as direct_router
from app.db.init_db import init_db

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title=settings.PROJECT_NAME,
    openapi_url="/openapi.json",
    docs_url="/docs",
    redoc_url="/redoc",
)

# Initialize database
try:
    logger.info("Initializing database...")
    init_db()
    logger.info("Database initialized successfully.")
except Exception as e:
    logger.error(f"Error initializing database: {e}")

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Add direct router for testing
app.include_router(direct_router, prefix="/api", tags=["test"])

# Include API router
app.include_router(api_router, prefix=settings.API_V1_STR)

# Try to include web router for the website
try:
    from app.web.controllers import router as web_router
    app.include_router(web_router)
    logger.info("Web router included successfully")
except ImportError as e:
    logger.warning(f"Web router import failed: {e}. Creating a placeholder router.")
    # Create a placeholder router if the web controllers are not available
    web_router = APIRouter()
    
    @web_router.get("/")
    async def web_root():
        return {"message": "Web interface is not available in this deployment"}
    
    app.include_router(web_router)

# Mount static files
try:
    app.mount("/static", StaticFiles(directory="app/static"), name="static")
except:
    # Static directory might not exist in development
    logger.warning("Static directory not found. Creating directory...")
    pass

# Create necessary directories
os.makedirs("app/data/files", exist_ok=True)
os.makedirs("app/data/embeddings", exist_ok=True)
os.makedirs("app/static/css", exist_ok=True)
os.makedirs("app/static/js", exist_ok=True)
os.makedirs("app/static/images", exist_ok=True)

@app.get("/")
async def root():
    """Root endpoint that redirects to the UI."""
    return {"message": "Welcome to Appraisal AI Agent. Navigate to /ui for the web interface."}

if __name__ == "__main__":
    uvicorn.run(
        "app.main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.DEBUG,
    )
