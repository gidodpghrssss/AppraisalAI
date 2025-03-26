from fastapi import APIRouter, HTTPException
from typing import Dict, Any
from app.agents.appraisal_agent import AppraisalAgent

router = APIRouter()
agent = AppraisalAgent()

@router.post("/analyze")
async def analyze_property(request: Dict[str, Any]):
    """
    Analyze a property using the AI agent
    """
    try:
        result = await agent.process_request(request)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/market-analysis")
async def get_market_analysis(location: str, property_type: str):
    """
    Get market analysis for a specific location and property type
    """
    try:
        result = await agent.analyze_market(location, property_type)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/estimate-value")
async def estimate_value(property_details: Dict[str, Any]):
    """
    Estimate property value
    """
    try:
        result = await agent.estimate_value(property_details)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
