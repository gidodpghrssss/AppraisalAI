"""
Property data service for fetching property information from various sources.
"""
import httpx
from typing import Dict, Any, List, Optional
import json
import os
from datetime import datetime

from app.core.config import settings
from app.services.web_search_service import WebSearchService

class PropertyDataService:
    """Service for retrieving property data from various sources."""
    
    def __init__(self, web_search_service: WebSearchService = None):
        """Initialize the property data service."""
        self.cadastre_api_url = settings.CADASTRE_API_URL
        self.market_data_api_url = settings.MARKET_DATA_API_URL
        self.web_search_service = web_search_service or WebSearchService()
        
        # Create cache directory if it doesn't exist
        os.makedirs("app/data/cache", exist_ok=True)
    
    async def get_property_details(self, property_id: str) -> Dict[str, Any]:
        """
        Get detailed information about a property.
        
        Args:
            property_id: The ID of the property to retrieve
            
        Returns:
            A dictionary containing property details
        """
        # Check cache first
        cached_data = self._check_cache(property_id)
        if cached_data:
            return cached_data
        
        # If not in cache, fetch from API
        try:
            # In a real implementation, this would call the actual cadastre API
            # For demo purposes, we'll return mock data
            property_data = await self._get_mock_property_data(property_id)
            
            # Cache the data
            self._cache_data(property_id, property_data)
            
            return property_data
        except Exception as e:
            raise Exception(f"Failed to retrieve property data: {str(e)}")
    
    async def get_comparable_properties(
        self, 
        location: str, 
        property_type: str,
        min_size: Optional[float] = None,
        max_size: Optional[float] = None,
        min_price: Optional[float] = None,
        max_price: Optional[float] = None,
        limit: int = 10
    ) -> List[Dict[str, Any]]:
        """
        Get comparable properties based on criteria.
        
        Args:
            location: The location to search in
            property_type: The type of property
            min_size: Minimum property size
            max_size: Maximum property size
            min_price: Minimum property price
            max_price: Maximum property price
            limit: Maximum number of results to return
            
        Returns:
            A list of comparable properties
        """
        # In a real implementation, this would call the market data API
        # For demo purposes, we'll return mock data
        comparables = await self._get_mock_comparables(
            location, 
            property_type,
            limit=limit
        )
        
        # Filter by criteria
        filtered_comparables = []
        for comp in comparables:
            if min_size and comp.get("size", 0) < min_size:
                continue
            if max_size and comp.get("size", 0) > max_size:
                continue
            if min_price and comp.get("price", 0) < min_price:
                continue
            if max_price and comp.get("price", 0) > max_price:
                continue
            filtered_comparables.append(comp)
        
        return filtered_comparables[:limit]
    
    async def get_market_trends(self, location: str, property_type: str) -> Dict[str, Any]:
        """
        Get market trends for a specific location and property type.
        
        Args:
            location: The location to get trends for
            property_type: The type of property
            
        Returns:
            Market trend data
        """
        # In a real implementation, this would call the market data API
        # For demo purposes, we'll return mock data
        cache_key = f"trends_{location}_{property_type}"
        cached_data = self._check_cache(cache_key)
        if cached_data:
            return cached_data
        
        # If not in cache, generate mock data
        trends = {
            "location": location,
            "property_type": property_type,
            "price_trends": {
                "last_month": 2.3,  # percentage change
                "last_quarter": 5.7,
                "last_year": 8.2
            },
            "inventory_trends": {
                "last_month": -1.5,  # percentage change
                "last_quarter": -3.2,
                "last_year": -7.8
            },
            "days_on_market": {
                "current": 32,
                "last_month": 35,
                "last_quarter": 40,
                "last_year": 45
            },
            "forecast": {
                "next_quarter": 2.1,  # predicted percentage change
                "next_year": 4.5
            }
        }
        
        # Cache the data
        self._cache_data(cache_key, trends)
        
        return trends
    
    async def search_property_regulations(self, location: str) -> List[Dict[str, Any]]:
        """
        Search for property regulations in a specific location.
        
        Args:
            location: The location to search regulations for
            
        Returns:
            A list of relevant regulations
        """
        # Use web search service to find regulations
        search_results = await self.web_search_service.search(
            f"property appraisal regulations in {location}"
        )
        
        # Process and return the results
        regulations = []
        for result in search_results[:5]:  # Limit to top 5 results
            regulations.append({
                "title": result.get("title", ""),
                "source": result.get("url", ""),
                "snippet": result.get("snippet", ""),
                "relevance": result.get("relevance", 0.0)
            })
        
        return regulations
    
    def _check_cache(self, key: str) -> Optional[Dict[str, Any]]:
        """Check if data is in cache and not expired."""
        cache_file = f"app/data/cache/{key}.json"
        if os.path.exists(cache_file):
            try:
                with open(cache_file, "r") as f:
                    data = json.load(f)
                
                # Check if cache is expired (24 hours)
                cache_time = datetime.fromisoformat(data.get("cache_time", "2000-01-01T00:00:00"))
                now = datetime.now()
                if (now - cache_time).total_seconds() < 86400:  # 24 hours
                    return data.get("data")
            except:
                pass
        
        return None
    
    def _cache_data(self, key: str, data: Dict[str, Any]) -> None:
        """Cache data with timestamp."""
        cache_file = f"app/data/cache/{key}.json"
        try:
            with open(cache_file, "w") as f:
                json.dump({
                    "data": data,
                    "cache_time": datetime.now().isoformat()
                }, f)
        except:
            # If caching fails, just continue without caching
            pass
    
    async def _get_mock_property_data(self, property_id: str) -> Dict[str, Any]:
        """Generate mock property data for demo purposes."""
        # Generate different data based on property_id to simulate different properties
        property_types = ["residential", "commercial", "industrial", "land"]
        property_type = property_types[hash(property_id) % len(property_types)]
        
        if property_type == "residential":
            return {
                "property_id": property_id,
                "type": "residential",
                "subtype": "single_family",
                "address": {
                    "street": "123 Main Street",
                    "city": "Metropolis",
                    "state": "NY",
                    "zip": "10001",
                    "country": "USA",
                    "coordinates": {
                        "latitude": 40.7128,
                        "longitude": -74.0060
                    }
                },
                "details": {
                    "size": 2500,  # square feet
                    "lot_size": 5000,  # square feet
                    "year_built": 1995,
                    "bedrooms": 4,
                    "bathrooms": 2.5,
                    "stories": 2,
                    "garage": True,
                    "garage_size": 2,  # cars
                    "basement": True,
                    "pool": False,
                    "condition": "good"
                },
                "valuation": {
                    "last_sale": {
                        "date": "2018-05-15",
                        "price": 450000
                    },
                    "tax_assessment": {
                        "year": 2023,
                        "value": 425000
                    },
                    "estimated_value": 520000
                },
                "legal": {
                    "owner": "John Doe",
                    "ownership_type": "fee_simple",
                    "zoning": "R1",
                    "encumbrances": ["mortgage"],
                    "restrictions": []
                }
            }
        elif property_type == "commercial":
            return {
                "property_id": property_id,
                "type": "commercial",
                "subtype": "retail",
                "address": {
                    "street": "456 Market Street",
                    "city": "Metropolis",
                    "state": "NY",
                    "zip": "10002",
                    "country": "USA",
                    "coordinates": {
                        "latitude": 40.7138,
                        "longitude": -74.0070
                    }
                },
                "details": {
                    "size": 5000,  # square feet
                    "lot_size": 7500,  # square feet
                    "year_built": 2005,
                    "stories": 1,
                    "parking_spaces": 20,
                    "condition": "excellent",
                    "frontage": 50  # feet
                },
                "valuation": {
                    "last_sale": {
                        "date": "2020-08-23",
                        "price": 1200000
                    },
                    "tax_assessment": {
                        "year": 2023,
                        "value": 1150000
                    },
                    "estimated_value": 1350000,
                    "income": {
                        "annual_rent": 120000,
                        "occupancy_rate": 0.95,
                        "expenses": 35000,
                        "cap_rate": 0.07
                    }
                },
                "legal": {
                    "owner": "Market Street LLC",
                    "ownership_type": "fee_simple",
                    "zoning": "C2",
                    "encumbrances": ["mortgage", "easement"],
                    "restrictions": ["signage"]
                },
                "tenants": [
                    {
                        "name": "Coffee Shop Inc.",
                        "lease_term": "5 years",
                        "lease_start": "2021-01-01",
                        "lease_end": "2025-12-31",
                        "monthly_rent": 5000
                    },
                    {
                        "name": "Bookstore LLC",
                        "lease_term": "3 years",
                        "lease_start": "2022-03-01",
                        "lease_end": "2025-02-28",
                        "monthly_rent": 4500
                    }
                ]
            }
        else:
            # Generic property data for other types
            return {
                "property_id": property_id,
                "type": property_type,
                "address": {
                    "street": f"{hash(property_id) % 999} Example Road",
                    "city": "Metropolis",
                    "state": "NY",
                    "zip": "10001",
                    "country": "USA"
                },
                "details": {
                    "size": hash(property_id) % 10000 + 1000,
                    "year_built": hash(property_id) % 50 + 1970
                },
                "valuation": {
                    "estimated_value": hash(property_id) % 1000000 + 200000
                }
            }
    
    async def _get_mock_comparables(
        self, 
        location: str, 
        property_type: str,
        limit: int = 10
    ) -> List[Dict[str, Any]]:
        """Generate mock comparable properties for demo purposes."""
        comparables = []
        
        # Generate a deterministic but varied set of comparables
        seed = hash(f"{location}_{property_type}")
        
        for i in range(limit):
            # Vary the properties slightly based on the seed and index
            price_base = 500000 if property_type == "residential" else 1200000
            size_base = 2500 if property_type == "residential" else 5000
            
            # Create variation in the comparables
            variation_factor = 0.8 + ((seed + i) % 40) / 100  # 0.8 to 1.2
            
            comp = {
                "id": f"comp_{seed}_{i}",
                "address": f"{100 + i} {location.title()} Ave",
                "type": property_type,
                "size": int(size_base * variation_factor),
                "year_built": 2000 - (i % 20),
                "price": int(price_base * variation_factor),
                "price_per_sqft": int((price_base * variation_factor) / (size_base * variation_factor)),
                "sale_date": f"2023-{(i % 12) + 1:02d}-{(i % 28) + 1:02d}",
                "distance": round(0.5 + i * 0.2, 1),  # miles from subject property
                "features": []
            }
            
            # Add type-specific details
            if property_type == "residential":
                comp["bedrooms"] = 3 + (i % 3)
                comp["bathrooms"] = 2 + (i % 2) + (0.5 if i % 2 == 0 else 0)
                comp["features"] = ["garage"] + (["pool"] if i % 3 == 0 else []) + (["basement"] if i % 2 == 0 else [])
            elif property_type == "commercial":
                comp["frontage"] = 40 + (i * 5)
                comp["parking_spaces"] = 15 + (i * 2)
                comp["cap_rate"] = round(0.06 + (i % 5) * 0.005, 3)
            
            comparables.append(comp)
        
        return comparables
