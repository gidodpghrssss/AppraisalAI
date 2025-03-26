from fastapi import APIRouter
from app.api.v1.endpoints import (
    appraisals,
    projects,
    analysis,
    reports,
    mobile,
    tools
)

api_router = APIRouter()

# Include all API endpoints
api_router.include_router(appraisals.router, prefix="/appraisals", tags=["appraisals"])
api_router.include_router(projects.router, prefix="/projects", tags=["projects"])
api_router.include_router(analysis.router, prefix="/analysis", tags=["analysis"])
api_router.include_router(reports.router, prefix="/reports", tags=["reports"])
api_router.include_router(mobile.router, prefix="/mobile", tags=["mobile"])
api_router.include_router(tools.router, prefix="/tools", tags=["tools"])
