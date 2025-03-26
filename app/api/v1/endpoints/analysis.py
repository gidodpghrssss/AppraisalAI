from fastapi import APIRouter, HTTPException
from typing import Dict, Any
from app.services.llm_service import LlamaService

router = APIRouter()
llm_service = LlamaService()

@router.post("/market")
async def analyze_market(location: str, property_type: str):
    """
    Analyze market conditions for a specific location and property type
    """
    try:
        result = await llm_service.get_market_insights(location, property_type)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/property")
async def analyze_property(property_details: Dict[str, Any]):
    """
    Analyze a property based on provided details
    """
    try:
        result = await llm_service.analyze_property(property_details)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/comparables")
async def find_comparables(property_id: str, radius_miles: float = 1.0, max_results: int = 5):
    """
    Find comparable properties for a given property
    """
    try:
        # This would typically query an external API or database
        # For now, return mock data
        return {
            "property_id": property_id,
            "comparables": [
                {
                    "id": "comp-001",
                    "address": "123 Similar St",
                    "sale_price": 450000,
                    "sale_date": "2025-01-15",
                    "similarity_score": 0.92
                },
                {
                    "id": "comp-002",
                    "address": "456 Nearby Ave",
                    "sale_price": 425000,
                    "sale_date": "2025-02-10",
                    "similarity_score": 0.87
                }
            ]
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
