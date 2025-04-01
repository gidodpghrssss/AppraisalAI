"""
Tool executor for the Appraisal AI Agent.
"""
import json
from typing import Dict, Any, List, Optional
import asyncio

from app.services.property_data_service import PropertyDataService
from app.services.web_search_service import WebSearchService

# Initialize services
property_service = PropertyDataService()
web_search_service = WebSearchService()

async def execute_tool(tool_name: str, args: Dict[str, Any]) -> Dict[str, Any]:
    """
    Execute a tool with the given arguments.
    
    Args:
        tool_name: Name of the tool to execute
        args: Arguments for the tool
        
    Returns:
        The result of the tool execution
    """
    # Parse arguments if they're a string
    if isinstance(args, str):
        try:
            args = json.loads(args)
        except:
            args = {}
    
    # Execute the appropriate tool
    if tool_name == "property_search":
        return await _execute_property_search(args)
    elif tool_name == "market_analysis":
        return await _execute_market_analysis(args)
    elif tool_name == "valuation_calculator":
        return await _execute_valuation_calculator(args)
    elif tool_name == "report_generator":
        return await _execute_report_generator(args)
    elif tool_name == "compliance_checker":
        return await _execute_compliance_checker(args)
    elif tool_name == "image_analyzer":
        return await _execute_image_analyzer(args)
    elif tool_name == "gis_mapper":
        return await _execute_gis_mapper(args)
    else:
        raise ValueError(f"Unknown tool: {tool_name}")

async def _execute_property_search(args: Dict[str, Any]) -> Dict[str, Any]:
    """Execute the property search tool."""
    location = args.get("location")
    property_type = args.get("property_type")
    min_price = args.get("min_price")
    max_price = args.get("max_price")
    min_size = args.get("min_size")
    max_size = args.get("max_size")
    limit = args.get("limit", 10)
    
    if not location or not property_type:
        raise ValueError("Location and property_type are required")
    
    # Get comparable properties
    comparables = await property_service.get_comparable_properties(
        location=location,
        property_type=property_type,
        min_size=min_size,
        max_size=max_size,
        min_price=min_price,
        max_price=max_price,
        limit=limit
    )
    
    return {
        "results": comparables,
        "count": len(comparables),
        "query": {
            "location": location,
            "property_type": property_type,
            "filters_applied": {
                "min_price": min_price,
                "max_price": max_price,
                "min_size": min_size,
                "max_size": max_size
            }
        }
    }

async def _execute_market_analysis(args: Dict[str, Any]) -> Dict[str, Any]:
    """Execute the market analysis tool."""
    location = args.get("location")
    property_type = args.get("property_type")
    include_trends = args.get("include_trends", True)
    include_regulations = args.get("include_regulations", False)
    
    if not location or not property_type:
        raise ValueError("Location and property_type are required")
    
    # Get market trends
    trends = await property_service.get_market_trends(
        location=location,
        property_type=property_type
    ) if include_trends else None
    
    # Get regulations
    regulations = await property_service.search_property_regulations(
        location=location
    ) if include_regulations else None
    
    return {
        "location": location,
        "property_type": property_type,
        "market_trends": trends,
        "regulations": regulations,
        "analysis_summary": f"Market analysis for {property_type} properties in {location} shows " +
                           f"{trends['price_trends']['last_year']}% price change over the last year " +
                           f"with an average of {trends['days_on_market']['current']} days on market."
                           if trends else "No trend data available."
    }

async def _execute_valuation_calculator(args: Dict[str, Any]) -> Dict[str, Any]:
    """Execute the valuation calculator tool."""
    property_id = args.get("property_id")
    method = args.get("method")
    adjustments = args.get("adjustments", {})
    
    if not property_id or not method:
        raise ValueError("Property ID and valuation method are required")
    
    # Get property details
    property_data = await property_service.get_property_details(property_id)
    
    # Calculate valuation based on method
    valuations = {}
    
    if method == "sales_comparison" or method == "all":
        # Get comparables for sales comparison approach
        comparables = await property_service.get_comparable_properties(
            location=property_data.get("address", {}).get("city", ""),
            property_type=property_data.get("type", ""),
            limit=5
        )
        
        # Calculate adjusted values of comparables
        adjusted_values = []
        for comp in comparables:
            # Apply adjustments (simplified for demo)
            adjusted_value = comp.get("price", 0)
            
            # Size adjustment
            if "size" in comp and "size" in property_data.get("details", {}):
                size_diff = property_data["details"]["size"] - comp["size"]
                size_adj = size_diff * (comp.get("price_per_sqft", 0))
                adjusted_value += size_adj
            
            # Other adjustments would go here
            
            adjusted_values.append(adjusted_value)
        
        # Calculate average of adjusted values
        sales_comparison_value = sum(adjusted_values) / len(adjusted_values) if adjusted_values else 0
        valuations["sales_comparison"] = round(sales_comparison_value, 2)
    
    if method == "cost" or method == "all":
        # Cost approach (simplified for demo)
        # Land value + (Replacement cost - Depreciation)
        if property_data.get("type") in ["residential", "commercial"]:
            # Simplified calculation
            year_built = property_data.get("details", {}).get("year_built", 2000)
            current_year = 2025  # Hardcoded current year for demo
            age = current_year - year_built
            
            # Replacement cost per square foot
            replacement_cost_per_sqft = 200 if property_data.get("type") == "residential" else 300
            
            # Calculate replacement cost
            size = property_data.get("details", {}).get("size", 0)
            replacement_cost = size * replacement_cost_per_sqft
            
            # Calculate depreciation (simplified linear depreciation)
            effective_life = 50  # years
            depreciation_rate = min(age / effective_life, 0.7)  # Cap at 70% depreciation
            depreciation = replacement_cost * depreciation_rate
            
            # Estimate land value (simplified)
            land_value = property_data.get("valuation", {}).get("estimated_value", 0) * 0.3
            
            # Calculate cost approach value
            cost_value = land_value + (replacement_cost - depreciation)
            valuations["cost"] = round(cost_value, 2)
    
    if method == "income" or method == "all":
        # Income approach (simplified for demo)
        if property_data.get("type") in ["commercial", "industrial"]:
            # Get income data from property
            income_data = property_data.get("valuation", {}).get("income", {})
            
            if income_data:
                annual_rent = income_data.get("annual_rent", 0)
                occupancy_rate = income_data.get("occupancy_rate", 0.9)
                expenses = income_data.get("expenses", 0)
                cap_rate = income_data.get("cap_rate", 0.07)
                
                # Calculate net operating income (NOI)
                effective_gross_income = annual_rent * occupancy_rate
                noi = effective_gross_income - expenses
                
                # Calculate value using direct capitalization
                if cap_rate > 0:
                    income_value = noi / cap_rate
                    valuations["income"] = round(income_value, 2)
    
    # Reconcile values if multiple methods used
    if method == "all":
        # Weighted average based on property type
        if property_data.get("type") == "residential":
            weights = {"sales_comparison": 0.7, "cost": 0.3, "income": 0.0}
        elif property_data.get("type") == "commercial":
            weights = {"sales_comparison": 0.3, "cost": 0.2, "income": 0.5}
        else:
            weights = {"sales_comparison": 0.5, "cost": 0.3, "income": 0.2}
        
        # Calculate weighted average
        reconciled_value = 0
        total_weight = 0
        
        for method_name, value in valuations.items():
            weight = weights.get(method_name, 0)
            if value > 0 and weight > 0:
                reconciled_value += value * weight
                total_weight += weight
        
        if total_weight > 0:
            reconciled_value = reconciled_value / total_weight
            valuations["reconciled"] = round(reconciled_value, 2)
    
    return {
        "property_id": property_id,
        "property_details": {
            "address": property_data.get("address", {}),
            "type": property_data.get("type", ""),
            "size": property_data.get("details", {}).get("size", 0)
        },
        "valuation_method": method,
        "valuations": valuations,
        "adjustments_applied": adjustments
    }

async def _execute_report_generator(args: Dict[str, Any]) -> Dict[str, Any]:
    """Execute the report generator tool."""
    property_id = args.get("property_id")
    report_type = args.get("report_type", "summary")
    include_sections = args.get("include_sections", [
        "property_description",
        "valuation",
        "reconciliation",
        "certification"
    ])
    
    if not property_id:
        raise ValueError("Property ID is required")
    
    # Get property details
    property_data = await property_service.get_property_details(property_id)
    
    # Generate report sections
    sections = {}
    
    if "property_description" in include_sections:
        sections["property_description"] = {
            "title": "Property Description",
            "content": f"The subject property is a {property_data.get('details', {}).get('size', 0)} square foot " +
                      f"{property_data.get('type')} property located at {property_data.get('address', {}).get('street')}, " +
                      f"{property_data.get('address', {}).get('city')}, {property_data.get('address', {}).get('state')}."
        }
    
    if "valuation" in include_sections:
        # Get valuation data
        valuation_data = await _execute_valuation_calculator({
            "property_id": property_id,
            "method": "all"
        })
        
        sections["valuation"] = {
            "title": "Valuation Analysis",
            "content": "The property has been valued using multiple approaches:",
            "data": valuation_data.get("valuations", {})
        }
    
    if "market_analysis" in include_sections:
        # Get market analysis
        market_data = await _execute_market_analysis({
            "location": property_data.get("address", {}).get("city", ""),
            "property_type": property_data.get("type", ""),
            "include_trends": True
        })
        
        sections["market_analysis"] = {
            "title": "Market Analysis",
            "content": market_data.get("analysis_summary", ""),
            "data": market_data.get("market_trends", {})
        }
    
    if "reconciliation" in include_sections:
        # Get reconciled value
        reconciled_value = valuation_data.get("valuations", {}).get("reconciled", 0) if "valuation" in include_sections else 0
        
        sections["reconciliation"] = {
            "title": "Reconciliation and Final Value Opinion",
            "content": f"After analyzing the property using multiple valuation approaches and " +
                      f"considering current market conditions, the final opinion of value for the subject property is " +
                      f"${reconciled_value:,.2f}.",
            "final_value": reconciled_value
        }
    
    if "certification" in include_sections:
        sections["certification"] = {
            "title": "Appraiser's Certification",
            "content": "I certify that, to the best of my knowledge and belief:\n" +
                      "1. The statements of fact contained in this report are true and correct.\n" +
                      "2. The reported analyses, opinions, and conclusions are limited only by the reported assumptions and limiting conditions and are my personal, impartial, and unbiased professional analyses, opinions, and conclusions.\n" +
                      "3. I have no present or prospective interest in the property that is the subject of this report and no personal interest with respect to the parties involved.\n" +
                      "4. I have performed no services, as an appraiser or in any other capacity, regarding the property that is the subject of this report within the three-year period immediately preceding acceptance of this assignment."
        }
    
    return {
        "report_id": f"report_{property_id}_{report_type}",
        "property_id": property_id,
        "report_type": report_type,
        "sections": sections,
        "summary": f"{report_type.title()} Appraisal Report for {property_data.get('address', {}).get('street')}, " +
                  f"{property_data.get('address', {}).get('city')}, {property_data.get('address', {}).get('state')}"
    }

async def _execute_compliance_checker(args: Dict[str, Any]) -> Dict[str, Any]:
    """Execute the compliance checker tool."""
    report_id = args.get("report_id")
    standards = args.get("standards", ["USPAP"])
    
    if not report_id:
        raise ValueError("Report ID is required")
    
    # In a real implementation, this would check the report against standards
    # For demo purposes, we'll return mock compliance results
    
    # Extract property_id from report_id
    property_id = report_id.split("_")[1] if "_" in report_id else "unknown"
    
    # Mock compliance checks
    compliance_results = {
        "USPAP": {
            "compliant": True,
            "missing_items": [],
            "recommendations": ["Add more detail to the scope of work section."]
        },
        "IVSC": {
            "compliant": True,
            "missing_items": ["Market analysis lacks global context"],
            "recommendations": ["Expand market analysis to include international factors."]
        },
        "local": {
            "compliant": True,
            "missing_items": [],
            "recommendations": []
        }
    }
    
    # Filter results to requested standards
    filtered_results = {std: compliance_results.get(std, {}) for std in standards}
    
    return {
        "report_id": report_id,
        "property_id": property_id,
        "standards_checked": standards,
        "compliance_results": filtered_results,
        "overall_compliant": all(result.get("compliant", False) for result in filtered_results.values()),
        "summary": "The report meets all essential requirements of the selected standards."
    }

async def _execute_image_analyzer(args: Dict[str, Any]) -> Dict[str, Any]:
    """Execute the image analyzer tool."""
    image_url = args.get("image_url")
    analysis_type = args.get("analysis_type")
    
    if not image_url or not analysis_type:
        raise ValueError("Image URL and analysis type are required")
    
    # In a real implementation, this would analyze the image
    # For demo purposes, we'll return mock analysis results
    
    # Mock image analysis results
    analysis_results = {}
    
    if analysis_type == "features" or analysis_type == "all":
        analysis_results["features"] = {
            "detected_features": [
                {"name": "hardwood_floors", "confidence": 0.92},
                {"name": "granite_countertops", "confidence": 0.87},
                {"name": "stainless_steel_appliances", "confidence": 0.95},
                {"name": "open_floor_plan", "confidence": 0.78}
            ],
            "room_type": "kitchen",
            "condition": "excellent"
        }
    
    if analysis_type == "damage" or analysis_type == "all":
        analysis_results["damage"] = {
            "detected_issues": [
                {"type": "water_damage", "severity": "minor", "confidence": 0.65, "location": "ceiling_corner"},
                {"type": "paint_peeling", "severity": "minimal", "confidence": 0.72, "location": "wall_near_window"}
            ],
            "overall_condition": "good",
            "estimated_repair_cost": 500
        }
    
    if analysis_type == "measurements" or analysis_type == "all":
        analysis_results["measurements"] = {
            "room_dimensions": {
                "width": 12.5,  # feet
                "length": 15.2,  # feet
                "height": 9.0,   # feet
                "area": 190.0    # square feet
            },
            "detected_objects": [
                {"type": "counter", "dimensions": {"width": 6.2, "depth": 2.5}},
                {"type": "island", "dimensions": {"width": 4.0, "depth": 3.0}},
                {"type": "doorway", "dimensions": {"width": 3.0, "height": 7.0}}
            ],
            "measurement_confidence": 0.85
        }
    
    return {
        "image_url": image_url,
        "analysis_type": analysis_type,
        "results": analysis_results,
        "summary": f"Image analysis complete with {len(analysis_results)} analysis types."
    }

async def _execute_gis_mapper(args: Dict[str, Any]) -> Dict[str, Any]:
    """Execute the GIS mapper tool."""
    location = args.get("location")
    map_type = args.get("map_type")
    radius = args.get("radius", 1.0)
    
    if not location or not map_type:
        raise ValueError("Location and map type are required")
    
    # In a real implementation, this would generate GIS maps
    # For demo purposes, we'll return mock map data
    
    # Mock coordinates based on location string
    # In a real implementation, this would use geocoding
    coordinates = {
        "latitude": 40.7128,
        "longitude": -74.0060
    }
    
    # Mock map data
    map_data = {
        "location": location,
        "coordinates": coordinates,
        "map_type": map_type,
        "radius": radius,
        "map_url": f"https://example.com/maps/{map_type}/{coordinates['latitude']},{coordinates['longitude']}/{radius}",
        "data_layers": []
    }
    
    # Add data layers based on map type
    if map_type == "property":
        map_data["data_layers"] = [
            {"name": "property_boundaries", "visible": True},
            {"name": "satellite_imagery", "visible": True},
            {"name": "street_view", "visible": True}
        ]
    elif map_type == "zoning":
        map_data["data_layers"] = [
            {"name": "zoning_districts", "visible": True},
            {"name": "property_boundaries", "visible": True},
            {"name": "land_use", "visible": True}
        ]
        map_data["zoning_info"] = {
            "current_zone": "R1 - Residential",
            "allowed_uses": ["single_family", "duplex"],
            "max_height": 35,  # feet
            "max_lot_coverage": 0.4  # 40%
        }
    elif map_type == "flood":
        map_data["data_layers"] = [
            {"name": "flood_zones", "visible": True},
            {"name": "property_boundaries", "visible": True},
            {"name": "elevation_contours", "visible": True}
        ]
        map_data["flood_info"] = {
            "flood_zone": "X",
            "in_floodplain": False,
            "base_flood_elevation": None,
            "last_flood_event": None
        }
    elif map_type == "value_heatmap":
        map_data["data_layers"] = [
            {"name": "property_values", "visible": True},
            {"name": "recent_sales", "visible": True},
            {"name": "neighborhood_boundaries", "visible": True}
        ]
        map_data["value_info"] = {
            "avg_value_per_sqft": 350,
            "value_trend": "+5.2% year-over-year",
            "hotspots": [
                {"name": "Downtown", "value_change": "+8.7%"},
                {"name": "Westside", "value_change": "+6.3%"}
            ]
        }
    elif map_type == "comparable_sales":
        map_data["data_layers"] = [
            {"name": "recent_sales", "visible": True},
            {"name": "property_boundaries", "visible": True},
            {"name": "subject_property", "visible": True}
        ]
        map_data["comparable_info"] = {
            "num_comparables": 8,
            "avg_sale_price": 425000,
            "avg_days_on_market": 28,
            "price_range": {
                "min": 375000,
                "max": 495000
            }
        }
    
    return map_data
