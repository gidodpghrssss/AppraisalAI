"""
Property management endpoints for the Appraisal AI Agent.
"""
from fastapi import APIRouter, HTTPException, Depends, File, UploadFile
from pydantic import BaseModel
from typing import List, Dict, Any, Optional
from datetime import datetime
import uuid

from app.services.dependencies import get_property_data_service

router = APIRouter()

# Mock database for properties (in a real app, this would be a database)
PROPERTIES_DB = {}

class PropertyBase(BaseModel):
    """Base model for property data."""
    address: Dict[str, Any]
    type: str
    subtype: Optional[str] = None
    details: Optional[Dict[str, Any]] = {}
    legal: Optional[Dict[str, Any]] = {}

class PropertyCreate(PropertyBase):
    """Model for creating a new property."""
    pass

class PropertyUpdate(BaseModel):
    """Model for updating a property."""
    address: Optional[Dict[str, Any]] = None
    type: Optional[str] = None
    subtype: Optional[str] = None
    details: Optional[Dict[str, Any]] = None
    legal: Optional[Dict[str, Any]] = None

class Property(PropertyBase):
    """Full property model with ID and timestamps."""
    id: str
    created_at: datetime
    updated_at: datetime
    valuation: Optional[Dict[str, Any]] = None
    images: Optional[List[Dict[str, Any]]] = []

@router.post("", response_model=Property)
async def create_property(property_data: PropertyCreate):
    """
    Create a new property.
    """
    property_id = str(uuid.uuid4())
    now = datetime.now()
    
    new_property = {
        **property_data.dict(),
        "id": property_id,
        "created_at": now,
        "updated_at": now,
        "images": []
    }
    
    PROPERTIES_DB[property_id] = new_property
    return new_property

@router.get("", response_model=List[Property])
async def list_properties(
    property_type: Optional[str] = None,
    city: Optional[str] = None,
    min_value: Optional[float] = None,
    max_value: Optional[float] = None
):
    """
    List all properties with optional filtering.
    """
    properties = list(PROPERTIES_DB.values())
    
    # Apply filters
    if property_type:
        properties = [p for p in properties if p["type"] == property_type]
    
    if city:
        properties = [p for p in properties if p.get("address", {}).get("city") == city]
    
    if min_value:
        properties = [p for p in properties if p.get("valuation", {}).get("estimated_value", 0) >= min_value]
    
    if max_value:
        properties = [p for p in properties if p.get("valuation", {}).get("estimated_value", 0) <= max_value]
    
    return properties

@router.get("/{property_id}", response_model=Property)
async def get_property(
    property_id: str,
    property_service = Depends(get_property_data_service)
):
    """
    Get a specific property by ID.
    """
    if property_id not in PROPERTIES_DB:
        raise HTTPException(status_code=404, detail="Property not found")
    
    property_data = PROPERTIES_DB[property_id]
    
    # Enrich with additional data from property service
    try:
        additional_data = await property_service.get_property_details(property_id)
        if additional_data:
            # Merge additional data with basic property data
            property_data.update({
                "additional_details": additional_data
            })
    except Exception:
        # If external service fails, still return basic property data
        pass
    
    return property_data

@router.put("/{property_id}", response_model=Property)
async def update_property(property_id: str, property_update: PropertyUpdate):
    """
    Update a property.
    """
    if property_id not in PROPERTIES_DB:
        raise HTTPException(status_code=404, detail="Property not found")
    
    current_property = PROPERTIES_DB[property_id]
    
    # Update fields that are provided
    update_data = property_update.dict(exclude_unset=True)
    
    for field, value in update_data.items():
        if isinstance(value, dict) and field in current_property and isinstance(current_property[field], dict):
            # Merge dictionaries for nested fields
            current_property[field].update(value)
        else:
            current_property[field] = value
    
    # Update the updated_at timestamp
    current_property["updated_at"] = datetime.now()
    
    PROPERTIES_DB[property_id] = current_property
    return current_property

@router.delete("/{property_id}")
async def delete_property(property_id: str):
    """
    Delete a property.
    """
    if property_id not in PROPERTIES_DB:
        raise HTTPException(status_code=404, detail="Property not found")
    
    del PROPERTIES_DB[property_id]
    return {"message": "Property deleted successfully"}

@router.post("/{property_id}/images")
async def upload_property_image(
    property_id: str,
    image: UploadFile = File(...),
    description: Optional[str] = None
):
    """
    Upload an image for a property.
    """
    if property_id not in PROPERTIES_DB:
        raise HTTPException(status_code=404, detail="Property not found")
    
    # In a real implementation, this would save the image to storage
    # For demo purposes, we'll just record the image metadata
    
    image_id = str(uuid.uuid4())
    now = datetime.now()
    
    image_data = {
        "id": image_id,
        "filename": image.filename,
        "content_type": image.content_type,
        "description": description,
        "uploaded_at": now,
        "url": f"/api/v1/properties/{property_id}/images/{image_id}"
    }
    
    # Add image to property
    if "images" not in PROPERTIES_DB[property_id]:
        PROPERTIES_DB[property_id]["images"] = []
    
    PROPERTIES_DB[property_id]["images"].append(image_data)
    PROPERTIES_DB[property_id]["updated_at"] = now
    
    return image_data

@router.get("/{property_id}/images")
async def list_property_images(property_id: str):
    """
    List all images for a property.
    """
    if property_id not in PROPERTIES_DB:
        raise HTTPException(status_code=404, detail="Property not found")
    
    return PROPERTIES_DB[property_id].get("images", [])

@router.get("/{property_id}/valuation", response_model=Dict[str, Any])
async def get_property_valuation(
    property_id: str,
    method: Optional[str] = "all",
    property_service = Depends(get_property_data_service)
):
    """
    Get valuation for a property.
    """
    if property_id not in PROPERTIES_DB:
        raise HTTPException(status_code=404, detail="Property not found")
    
    property_data = PROPERTIES_DB[property_id]
    
    # Get valuation from property service
    try:
        if method == "all":
            # Get all valuation methods
            sales_comparison = await property_service.calculate_valuation(property_id, "sales_comparison")
            cost_approach = await property_service.calculate_valuation(property_id, "cost_approach")
            income_approach = await property_service.calculate_valuation(property_id, "income_approach")
            
            return {
                "sales_comparison": sales_comparison,
                "cost_approach": cost_approach,
                "income_approach": income_approach,
                "recommended_value": (sales_comparison["value"] + cost_approach["value"] + income_approach["value"]) / 3
            }
        else:
            # Get specific valuation method
            valuation = await property_service.calculate_valuation(property_id, method)
            return {method: valuation}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error calculating valuation: {str(e)}")

@router.get("/{property_id}/comparables", response_model=Dict[str, Any])
async def get_property_comparables(
    property_id: str,
    limit: Optional[int] = 5,
    property_service = Depends(get_property_data_service)
):
    """
    Get comparable properties for a property.
    """
    if property_id not in PROPERTIES_DB:
        raise HTTPException(status_code=404, detail="Property not found")
    
    property_data = PROPERTIES_DB[property_id]
    
    # Get location from property data
    location = property_data["address"].get("city", "") + ", " + property_data["address"].get("state", "")
    property_type = property_data["type"]
    
    # Get comparables from property service
    try:
        comparables = await property_service.get_comparable_properties(
            location=location,
            property_type=property_type,
            limit=limit
        )
        
        return {
            "property_id": property_id,
            "location": location,
            "property_type": property_type,
            "comparables": comparables,
            "count": len(comparables)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error finding comparable properties: {str(e)}")

@router.get("/{property_id}/market-analysis", response_model=Dict[str, Any])
async def get_property_market_analysis(
    property_id: str,
    property_service = Depends(get_property_data_service)
):
    """
    Get market analysis for a property's location.
    """
    if property_id not in PROPERTIES_DB:
        raise HTTPException(status_code=404, detail="Property not found")
    
    property_data = PROPERTIES_DB[property_id]
    
    # Get location from property data
    location = property_data["address"].get("city", "") + ", " + property_data["address"].get("state", "")
    property_type = property_data["type"]
    
    # Get market analysis from property service
    try:
        market_trends = await property_service.get_market_trends(
            location=location,
            property_type=property_type
        )
        
        return {
            "property_id": property_id,
            "location": location,
            "property_type": property_type,
            "market_trends": market_trends,
            "analysis_date": datetime.now().isoformat()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving market analysis: {str(e)}")
