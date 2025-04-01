"""
API router for the Appraisal AI Agent.
"""
from fastapi import APIRouter

from app.api.v1 import health, agent, projects, properties, reports, clients, website, admin, rag

# Create the main API router
api_router = APIRouter()

# Include routers for different endpoints
api_router.include_router(health.router, prefix="/health", tags=["health"])
api_router.include_router(agent.router, prefix="/agent", tags=["agent"])
api_router.include_router(projects.router, prefix="/projects", tags=["projects"])
api_router.include_router(properties.router, prefix="/properties", tags=["properties"])
api_router.include_router(reports.router, prefix="/reports", tags=["reports"])
api_router.include_router(clients.router, prefix="/clients", tags=["clients"])
api_router.include_router(website.router, prefix="/website", tags=["website"])
api_router.include_router(admin.router, prefix="/admin", tags=["admin"])
api_router.include_router(rag.router, prefix="/rag", tags=["rag"])

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
