"""
Tool registry for the Appraisal AI Agent.
"""
from typing import List, Dict, Any, Optional

# Define the tools available to the agent
AVAILABLE_TOOLS = {
    "property_search": {
        "type": "function",
        "function": {
            "name": "property_search",
            "description": "Search for properties based on criteria",
            "parameters": {
                "type": "object",
                "properties": {
                    "location": {
                        "type": "string",
                        "description": "Location to search in (city, neighborhood, etc.)"
                    },
                    "property_type": {
                        "type": "string",
                        "description": "Type of property (residential, commercial, industrial, land)",
                        "enum": ["residential", "commercial", "industrial", "land"]
                    },
                    "min_price": {
                        "type": "number",
                        "description": "Minimum price"
                    },
                    "max_price": {
                        "type": "number",
                        "description": "Maximum price"
                    },
                    "min_size": {
                        "type": "number",
                        "description": "Minimum size in square feet"
                    },
                    "max_size": {
                        "type": "number",
                        "description": "Maximum size in square feet"
                    },
                    "limit": {
                        "type": "integer",
                        "description": "Maximum number of results to return",
                        "default": 10
                    }
                },
                "required": ["location", "property_type"]
            }
        }
    },
    "market_analysis": {
        "type": "function",
        "function": {
            "name": "market_analysis",
            "description": "Get market analysis for a location and property type",
            "parameters": {
                "type": "object",
                "properties": {
                    "location": {
                        "type": "string",
                        "description": "Location to analyze (city, neighborhood, etc.)"
                    },
                    "property_type": {
                        "type": "string",
                        "description": "Type of property (residential, commercial, industrial, land)",
                        "enum": ["residential", "commercial", "industrial", "land"]
                    },
                    "include_trends": {
                        "type": "boolean",
                        "description": "Whether to include market trends",
                        "default": True
                    },
                    "include_regulations": {
                        "type": "boolean",
                        "description": "Whether to include regulatory information",
                        "default": False
                    }
                },
                "required": ["location", "property_type"]
            }
        }
    },
    "valuation_calculator": {
        "type": "function",
        "function": {
            "name": "valuation_calculator",
            "description": "Calculate property valuation using different methods",
            "parameters": {
                "type": "object",
                "properties": {
                    "property_id": {
                        "type": "string",
                        "description": "ID of the property to value"
                    },
                    "method": {
                        "type": "string",
                        "description": "Valuation method to use",
                        "enum": ["sales_comparison", "cost", "income", "all"]
                    },
                    "adjustments": {
                        "type": "object",
                        "description": "Adjustments to apply to the valuation"
                    }
                },
                "required": ["property_id", "method"]
            }
        }
    },
    "report_generator": {
        "type": "function",
        "function": {
            "name": "report_generator",
            "description": "Generate an appraisal report for a property",
            "parameters": {
                "type": "object",
                "properties": {
                    "property_id": {
                        "type": "string",
                        "description": "ID of the property to generate a report for"
                    },
                    "report_type": {
                        "type": "string",
                        "description": "Type of report to generate",
                        "enum": ["full", "summary", "restricted"]
                    },
                    "include_sections": {
                        "type": "array",
                        "description": "Sections to include in the report",
                        "items": {
                            "type": "string",
                            "enum": [
                                "property_description",
                                "market_analysis",
                                "valuation",
                                "comparables",
                                "income_analysis",
                                "cost_analysis",
                                "reconciliation",
                                "certification"
                            ]
                        }
                    }
                },
                "required": ["property_id", "report_type"]
            }
        }
    },
    "compliance_checker": {
        "type": "function",
        "function": {
            "name": "compliance_checker",
            "description": "Check if an appraisal report complies with regulations",
            "parameters": {
                "type": "object",
                "properties": {
                    "report_id": {
                        "type": "string",
                        "description": "ID of the report to check"
                    },
                    "standards": {
                        "type": "array",
                        "description": "Standards to check compliance against",
                        "items": {
                            "type": "string",
                            "enum": ["USPAP", "IVSC", "local"]
                        }
                    }
                },
                "required": ["report_id"]
            }
        }
    },
    "image_analyzer": {
        "type": "function",
        "function": {
            "name": "image_analyzer",
            "description": "Analyze property images for features, damage, or measurements",
            "parameters": {
                "type": "object",
                "properties": {
                    "image_url": {
                        "type": "string",
                        "description": "URL of the image to analyze"
                    },
                    "analysis_type": {
                        "type": "string",
                        "description": "Type of analysis to perform",
                        "enum": ["features", "damage", "measurements", "all"]
                    }
                },
                "required": ["image_url", "analysis_type"]
            }
        }
    },
    "gis_mapper": {
        "type": "function",
        "function": {
            "name": "gis_mapper",
            "description": "Generate GIS maps and spatial analysis for properties",
            "parameters": {
                "type": "object",
                "properties": {
                    "location": {
                        "type": "string",
                        "description": "Location to map (address, coordinates, or area)"
                    },
                    "map_type": {
                        "type": "string",
                        "description": "Type of map to generate",
                        "enum": ["property", "zoning", "flood", "value_heatmap", "comparable_sales"]
                    },
                    "radius": {
                        "type": "number",
                        "description": "Radius in miles around the location",
                        "default": 1.0
                    }
                },
                "required": ["location", "map_type"]
            }
        }
    }
}

def get_available_tools(tool_names: List[str]) -> List[Dict[str, Any]]:
    """
    Get the tool definitions for the specified tool names.
    
    Args:
        tool_names: List of tool names to retrieve
        
    Returns:
        List of tool definitions
    """
    tools = []
    for name in tool_names:
        if name in AVAILABLE_TOOLS:
            tools.append(AVAILABLE_TOOLS[name])
    
    return tools
