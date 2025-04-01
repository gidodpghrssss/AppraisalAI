"""
Direct API endpoints for testing.
"""
from fastapi import APIRouter, Depends
from pydantic import BaseModel
from datetime import datetime

router = APIRouter()

class TestResponse(BaseModel):
    """Test response model."""
    status: str
    message: str
    timestamp: str

@router.get("/test", response_model=TestResponse)
async def test_endpoint():
    """
    Test endpoint to verify API functionality.
    """
    return TestResponse(
        status="ok",
        message="Direct API endpoint is working correctly",
        timestamp=datetime.now().isoformat()
    )
