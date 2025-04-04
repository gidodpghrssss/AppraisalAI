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
import sys

from app.core.config import settings
from app.api.v1.api import api_router
from app.api.direct import router as direct_router
from app.db.init_db import init_db
from app.db.session import engine, SessionLocal

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title=settings.PROJECT_NAME,
    openapi_url="/openapi.json",
    docs_url="/docs",
    redoc_url="/redoc",
    description="""
    Appraisal AI Agent API
    
    This API provides access to the Appraisal AI Agent, which helps real estate appraisers with:
    
    - Property valuation using multiple methods
    - Market analysis and data interpretation
    - Report generation and quality control
    - Project management
    
    The API is organized into several endpoints for different functionalities.
    """
)

# Initialize database
try:
    logger.info("Initializing database...")
    init_db()
    logger.info("Database initialized successfully.")
except Exception as e:
    logger.error(f"Error initializing database: {e}")

# Run database migrations
logger.info("Running database migrations...")
try:
    from sqlalchemy import text
    
    # Get database URL from settings
    DATABASE_URL = settings.DATABASE_URL
    
    # Create a database session
    db = SessionLocal()
    
    # Check if we're using PostgreSQL
    if "postgresql" in DATABASE_URL:
        logger.info("PostgreSQL database detected, checking for schema issues")
        
        # Fix projects table schema issues
        try:
            # Check if title column exists
            check_column_sql = """
            SELECT EXISTS (
                SELECT FROM information_schema.columns 
                WHERE table_name = 'projects' AND column_name = 'title'
            );
            """
            title_exists = db.execute(text(check_column_sql)).scalar()
            
            if not title_exists:
                logger.info("Adding title column to projects table")
                db.execute(text("ALTER TABLE projects ADD COLUMN title VARCHAR(255);"))
                db.commit()
            
            # Check if client_id column type
            check_column_sql = """
            SELECT data_type FROM information_schema.columns 
            WHERE table_name = 'projects' AND column_name = 'client_id';
            """
            result = db.execute(text(check_column_sql)).fetchone()
            
            if result:
                data_type = result[0]
                logger.info(f"client_id column exists with type: {data_type}")
                
                if data_type == 'character varying':
                    logger.info("Converting client_id from VARCHAR to INTEGER")
                    # Create a temporary column
                    db.execute(text("ALTER TABLE projects ADD COLUMN client_id_temp INTEGER;"))
                    # Try to convert existing values
                    db.execute(text("UPDATE projects SET client_id_temp = client_id::INTEGER WHERE client_id ~ '^[0-9]+$';"))
                    # Drop the old column
                    db.execute(text("ALTER TABLE projects DROP COLUMN client_id;"))
                    # Rename the temp column
                    db.execute(text("ALTER TABLE projects RENAME COLUMN client_id_temp TO client_id;"))
                    db.commit()
            
            # Check if property_id column type
            check_column_sql = """
            SELECT data_type FROM information_schema.columns 
            WHERE table_name = 'projects' AND column_name = 'property_id';
            """
            result = db.execute(text(check_column_sql)).fetchone()
            
            if result:
                data_type = result[0]
                logger.info(f"property_id column exists with type: {data_type}")
                
                if data_type == 'character varying':
                    logger.info("Converting property_id from VARCHAR to INTEGER")
                    # Create a temporary column
                    db.execute(text("ALTER TABLE projects ADD COLUMN property_id_temp INTEGER;"))
                    # Try to convert existing values
                    db.execute(text("UPDATE projects SET property_id_temp = property_id::INTEGER WHERE property_id ~ '^[0-9]+$';"))
                    # Drop the old column
                    db.execute(text("ALTER TABLE projects DROP COLUMN property_id;"))
                    # Rename the temp column
                    db.execute(text("ALTER TABLE projects RENAME COLUMN property_id_temp TO property_id;"))
                    db.commit()
            
            logger.info("Database migration completed successfully")
        except Exception as e:
            logger.error(f"Error during database migration: {e}")
            db.rollback()
    else:
        logger.info("Not using PostgreSQL, skipping database migration")
    
    # Close the database session
    db.close()
except Exception as e:
    logger.error(f"Failed to run database migrations: {e}")

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

# Create necessary directories
os.makedirs("app/data/files", exist_ok=True)
os.makedirs("app/data/embeddings", exist_ok=True)
os.makedirs("app/static/css", exist_ok=True)
os.makedirs("app/static/js", exist_ok=True)
os.makedirs("app/static/images", exist_ok=True)

# Try to include web router for the website with better error handling
try:
    from app.web.controllers import router as web_router
    
    # Check if templates directory exists
    templates_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "templates")
    if os.path.exists(templates_dir):
        logger.info(f"Templates directory found at: {templates_dir}")
        
        # Mount static files if they exist
        static_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "static")
        if os.path.exists(static_dir):
            app.mount("/static", StaticFiles(directory=static_dir), name="static")
            logger.info(f"Static files mounted from: {static_dir}")
        else:
            # Create static directory if it doesn't exist
            os.makedirs(static_dir, exist_ok=True)
            app.mount("/static", StaticFiles(directory=static_dir), name="static")
            logger.info(f"Created and mounted static directory at: {static_dir}")
        
        # Include the web router
        app.include_router(web_router)
        logger.info("Web router included successfully")
    else:
        logger.warning(f"Templates directory not found at: {templates_dir}")
        # Try to create templates directory
        try:
            os.makedirs(templates_dir, exist_ok=True)
            logger.info(f"Created templates directory at: {templates_dir}")
            app.include_router(web_router)
            logger.info("Web router included after creating templates directory")
        except Exception as e:
            logger.error(f"Failed to create templates directory: {e}")
            raise ImportError("Templates directory not found and could not be created")
        
except ImportError as e:
    logger.warning(f"Web router import failed: {e}. Creating a placeholder router.")
    # Create a placeholder router if the web controllers are not available
    web_router = APIRouter()
    
    @web_router.get("/")
    async def web_root():
        return {"message": "Web interface is not available in this deployment. Please check logs for details."}
    
    app.include_router(web_router)

@app.get("/")
async def root():
    """Root endpoint that redirects to the UI."""
    return {
        "message": "Welcome to Appraisal AI Agent",
        "documentation": "/docs",
        "api": "/api/v1",
        "status": "running"
    }

if __name__ == "__main__":
    uvicorn.run(
        "app.main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.DEBUG,
    )
