from fastapi import APIRouter, HTTPException
from app.core.config import settings
import requests
from openai import OpenAI

router = APIRouter()

@router.get("/health", tags=["health"])
async def health_check():
    try:
        # Check database connection
        # Add your database health check logic here
        
        # Check Nebius API connection
        try:
            client = OpenAI(
                base_url=settings.NEBIUS_API_URL,
                api_key=settings.NEBIUS_API_KEY
            )
            # Simple request to check if API is accessible
            client.models.list()
            nebius_status = "ok"
        except Exception as e:
            nebius_status = "unavailable"
            
        return {
            "status": "ok" if nebius_status == "ok" else "warning",
            "services": {
                "database": "ok",
                "nebius_api": nebius_status
            },
            "version": settings.VERSION
        }
        
    except Exception as e:
        raise HTTPException(status_code=503, detail=str(e))
