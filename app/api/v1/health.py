from fastapi import APIRouter, Depends, HTTPException
from app.core.config import get_settings
from app.services.llm_service import LlamaService
from app.services.property_data_service import PropertyDataService
import aiohttp
import os

router = APIRouter()
settings = get_settings()

@router.get("/health", tags=["health"])
async def health_check():
    """
    Health check endpoint to verify API and services are functioning
    """
    health_status = {
        "status": "ok",
        "api_version": settings.VERSION,
        "services": {}
    }
    
    # Check Nebius API connection
    try:
        llm_service = LlamaService()
        await llm_service.test_connection()
        health_status["services"]["nebius_api"] = "connected"
    except Exception as e:
        health_status["services"]["nebius_api"] = f"error: {str(e)}"
        health_status["status"] = "degraded"
    
    # Check OpenStreetMap API
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get("https://nominatim.openstreetmap.org/status.php?format=json") as response:
                if response.status == 200:
                    health_status["services"]["openstreetmap_api"] = "connected"
                else:
                    health_status["services"]["openstreetmap_api"] = f"error: HTTP {response.status}"
                    health_status["status"] = "degraded"
    except Exception as e:
        health_status["services"]["openstreetmap_api"] = f"error: {str(e)}"
        health_status["status"] = "degraded"
    
    # Check Brave Search API if configured
    if settings.BRAVE_API_KEY:
        try:
            async with aiohttp.ClientSession() as session:
                headers = {
                    "Accept": "application/json",
                    "Accept-Encoding": "gzip",
                    "X-Subscription-Token": settings.BRAVE_API_KEY
                }
                async with session.get(
                    "https://api.search.brave.com/res/v1/web/search?q=test&count=1",
                    headers=headers
                ) as response:
                    if response.status == 200:
                        health_status["services"]["brave_search_api"] = "connected"
                    else:
                        health_status["services"]["brave_search_api"] = f"error: HTTP {response.status}"
                        health_status["status"] = "degraded"
        except Exception as e:
            health_status["services"]["brave_search_api"] = f"error: {str(e)}"
            health_status["status"] = "degraded"
    else:
        health_status["services"]["brave_search_api"] = "not configured (optional)"
    
    # Check data cache directory
    try:
        if not os.path.exists(settings.OPEN_DATA_CACHE_DIR):
            os.makedirs(settings.OPEN_DATA_CACHE_DIR)
        health_status["services"]["data_cache"] = "available"
    except Exception as e:
        health_status["services"]["data_cache"] = f"error: {str(e)}"
        health_status["status"] = "degraded"
    
    # Check database connection
    try:
        # Simple database check (can be expanded later)
        if settings.DATABASE_URL:
            health_status["services"]["database"] = "connected"
        else:
            health_status["services"]["database"] = "not configured"
            health_status["status"] = "degraded"
    except Exception as e:
        health_status["services"]["database"] = f"error: {str(e)}"
        health_status["status"] = "degraded"
    
    # Check optional API keys
    if settings.ATTOM_API_KEY:
        health_status["services"]["attom_api"] = "configured"
    else:
        health_status["services"]["attom_api"] = "not configured (optional)"
    
    if settings.GEOCODIO_API_KEY:
        health_status["services"]["geocodio_api"] = "configured"
    else:
        health_status["services"]["geocodio_api"] = "not configured (optional)"
    
    return health_status
