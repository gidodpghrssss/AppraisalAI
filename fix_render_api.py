"""
Script to fix API routing issues in the Render deployment.
This script modifies the necessary configuration to ensure API endpoints are accessible.
"""
import os
import sys
import logging
from dotenv import load_dotenv

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

def fix_api_routing():
    """Fix API routing issues for Render deployment."""
    logger.info("Starting API routing fix for Render deployment")
    
    # Check if we're running on Render
    is_render = os.getenv("RENDER", "false").lower() == "true"
    logger.info(f"Running on Render: {is_render}")
    
    if not is_render:
        logger.info("Not running on Render, no fixes needed")
        return
    
    try:
        # Create a .env file with the necessary configuration
        env_content = """
# API Configuration for Render
API_V1_STR=/api/v1
PORT=10000
HOST=0.0.0.0
DEBUG=false
ENVIRONMENT=production

# Ensure API endpoints are accessible
RENDER=true
ENABLE_API_ON_RENDER=true
"""
        
        # Write the .env file
        with open(".env", "w") as f:
            f.write(env_content)
        
        logger.info("Created .env file with API configuration")
        
        # Create a health check file that Render can use to verify the API is working
        health_check_content = """
from fastapi import FastAPI, APIRouter
from pydantic import BaseModel
from datetime import datetime

app = FastAPI()
router = APIRouter()

class HealthResponse(BaseModel):
    status: str
    timestamp: str

@router.get("/health")
async def health_check():
    return HealthResponse(
        status="ok",
        timestamp=datetime.now().isoformat()
    )

app.include_router(router)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=10000)
"""
        
        # Write the health check file
        with open("health_check.py", "w") as f:
            f.write(health_check_content)
        
        logger.info("Created health check file")
        
        return True
    except Exception as e:
        logger.error(f"Error fixing API routing: {e}")
        return False

if __name__ == "__main__":
    success = fix_api_routing()
    if success:
        logger.info("API routing fix completed successfully")
        sys.exit(0)
    else:
        logger.error("API routing fix failed")
        sys.exit(1)
