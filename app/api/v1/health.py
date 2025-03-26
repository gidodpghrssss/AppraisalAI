from fastapi import APIRouter, HTTPException
from app.core.config import settings
import requests

router = APIRouter()

@router.get("/health", tags=["health"])
async def health_check():
    try:
        # Check database connection
        # Add your database health check logic here
        
        # Check Llama Stack connection
        try:
            response = requests.get(f"{settings.LLAMA_API_URL}/health")
            response.raise_for_status()
        except Exception as e:
            return {
                "status": "warning",
                "services": {
                    "database": "ok",
                    "llama_stack": "unavailable"
                }
            }
            
        return {
            "status": "ok",
            "services": {
                "database": "ok",
                "llama_stack": "ok"
            }
        }
        
    except Exception as e:
        raise HTTPException(status_code=503, detail=str(e))
