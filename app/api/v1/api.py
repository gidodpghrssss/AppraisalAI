"""
API router for the Appraisal AI Agent.
"""
from fastapi import APIRouter
import logging

logger = logging.getLogger(__name__)

# Create the main API router
api_router = APIRouter()

# Import health module - this should always be available
from app.api.v1 import health
api_router.include_router(health.router, prefix="/health", tags=["health"])

# Try to import other modules, but don't fail if they're not available
try:
    from app.api.v1 import agent
    api_router.include_router(agent.router, prefix="/agent", tags=["agent"])
    logger.info("Agent router included successfully")
except ImportError as e:
    logger.warning(f"Agent router import failed: {e}")

try:
    from app.api.v1 import projects
    api_router.include_router(projects.router, prefix="/projects", tags=["projects"])
    logger.info("Projects router included successfully")
except ImportError as e:
    logger.warning(f"Projects router import failed: {e}")

try:
    from app.api.v1 import properties
    api_router.include_router(properties.router, prefix="/properties", tags=["properties"])
    logger.info("Properties router included successfully")
except ImportError as e:
    logger.warning(f"Properties router import failed: {e}")

try:
    from app.api.v1 import reports
    api_router.include_router(reports.router, prefix="/reports", tags=["reports"])
    logger.info("Reports router included successfully")
except ImportError as e:
    logger.warning(f"Reports router import failed: {e}")

try:
    from app.api.v1 import clients
    api_router.include_router(clients.router, prefix="/clients", tags=["clients"])
    logger.info("Clients router included successfully")
except ImportError as e:
    logger.warning(f"Clients router import failed: {e}")

try:
    from app.api.v1 import website
    api_router.include_router(website.router, prefix="/website", tags=["website"])
    logger.info("Website router included successfully")
except ImportError as e:
    logger.warning(f"Website router import failed: {e}")

try:
    from app.api.v1 import admin
    api_router.include_router(admin.router, prefix="/admin", tags=["admin"])
    logger.info("Admin router included successfully")
except ImportError as e:
    logger.warning(f"Admin router import failed: {e}")

try:
    from app.api.v1 import rag
    api_router.include_router(rag.router, prefix="/rag", tags=["rag"])
    logger.info("RAG router included successfully")
except ImportError as e:
    logger.warning(f"RAG router import failed: {e}")

# Add a direct health check endpoint at the API root
@api_router.get("/", tags=["root"])
async def api_root():
    """
    API root endpoint.
    """
    return {
        "status": "ok",
        "message": "Appraisal AI API is running",
        "version": "1.0.0"
    }
