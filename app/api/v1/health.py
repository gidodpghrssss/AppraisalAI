"""
Health check endpoints for the Appraisal AI Agent.
"""
from fastapi import APIRouter, Depends
from pydantic import BaseModel
from datetime import datetime

from app.core.config import settings

# Try to import the LLM service, but provide a fallback if it's not available
try:
    from app.services.dependencies import get_llm_service
    has_llm_service = True
except ImportError:
    has_llm_service = False

router = APIRouter()

class HealthResponse(BaseModel):
    """Health check response model."""
    status: str
    version: str
    environment: str
    timestamp: str
    llm_status: str

@router.get("/", response_model=HealthResponse)
async def health_check(llm_service=None):
    """
    Health check endpoint.
    Returns the status of the API and its dependencies.
    """
    # Check LLM service status
    llm_status = "unknown"
    
    if has_llm_service:
        try:
            # Only try to get the LLM service if the import was successful
            if llm_service is None:
                from app.services.dependencies import get_llm_service
                llm_service = get_llm_service()
            
            await llm_service.check_connection()
            llm_status = "ok"
        except Exception as e:
            llm_status = f"error: {str(e)}"
    
    return HealthResponse(
        status="ok",
        version="1.0.0",
        environment=settings.ENVIRONMENT,
        timestamp=datetime.now().isoformat(),
        llm_status=llm_status
    )

@router.get("/ping", response_model=dict)
async def ping():
    """
    Simple ping endpoint for health checks.
    """
    return {"status": "ok", "message": "pong"}
