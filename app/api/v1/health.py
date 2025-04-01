"""
Health check endpoints for the Appraisal AI Agent.
"""
from fastapi import APIRouter, Depends
from pydantic import BaseModel
from datetime import datetime

from app.core.config import settings
from app.services.dependencies import get_llm_service

router = APIRouter()

class HealthResponse(BaseModel):
    """Health check response model."""
    status: str
    version: str
    environment: str
    timestamp: str
    llm_status: str

@router.get("/", response_model=HealthResponse)
async def health_check(llm_service = Depends(get_llm_service)):
    """
    Health check endpoint.
    Returns the status of the API and its dependencies.
    """
    # Check LLM service status
    llm_status = "ok"
    try:
        await llm_service.check_connection()
    except Exception:
        llm_status = "error"
    
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
