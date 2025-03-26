import os
import json
import requests
import hashlib
from typing import Dict, Any, Optional, List
from app.core.config import settings
from app.services.web_search_service import WebSearchService

class PropertyDataService:
    """Service for accessing free property data sources"""
    
    def __init__(self):
        # Create cache directory if it doesn't exist
        os.makedirs(settings.OPEN_DATA_CACHE_DIR, exist_ok=True)
        self.web_search_service = WebSearchService()
    
    async def get_property_data(self, property_id: str) -> Dict[str, Any]:
        """Get property data from available sources"""
        # Check cache first
        cached_data = self._get_from_cache(property_id)
        if cached_data:
            return cached_data
            
        # Try different data sources
        if property_id.startswith("osm-"):
            # OpenStreetMap data
            osm_id = property_id.replace("osm-", "")
            data = await self._get_osm_data(osm_id)
        elif property_id.startswith("geo-"):
            # Geocodio data (free tier)
            address = property_id.replace("geo-", "")
            data = await self._get_geocodio_data(address)
        elif property_id.startswith("attom-"):
            # ATTOM data (free tier)
            attom_id = property_id.replace("attom-", "")
            data = await self._get_attom_data(attom_id)
        elif property_id.startswith("web-"):
            # Web search data
            address = property_id.replace("web-", "")
            data = await self._get_web_search_data(address)
        else:
            # Generate mock data for development
            data = self._generate_mock_data(property_id)
            
        # Cache the data
        self._save_to_cache(property_id, data)
        return data
    
    async def search_properties(self, query: str, location: str = None, property_type: str = None) -> List[Dict[str, Any]]:
        """Search for properties using available sources"""
        # Try to get data from web search first if we have an address
        if query and location and settings.BRAVE_API_KEY:
            try:
                web_data = await self.web_search_service.search_property_info(query, location)
                if web_data and "address" in web_data:
                    # Create a property ID for the web search result
                    property_id = f"web-{web_data['address']}"
                    
                    # Cache the data
                    self._save_to_cache(property_id, web_data)
                    
                    return [{
                        "property_id": property_id,
                        "address": web_data.get("address", ""),
                        "property_type": property_type or "unknown",
                        "estimated_value": web_data.get("estimated_value", 0),
                        "source": "web_search"
                    }]
            except Exception as e:
                print(f"Error searching with web search: {str(e)}")
        
        # For development, generate mock search results
        results = []
        
        # Generate a deterministic set of results based on the query
        seed = hashlib.md5(query.encode()).hexdigest()
        num_results = min(5, max(1, int(seed[0], 16)))
        
        for i in range(num_results):
            property_id = f"prop-{seed[:8]}-{i}"
            
            # Create property data with some relation to the query
            property_types = ["residential", "commercial", "industrial", "land"]
            if property_type and property_type in property_types:
                selected_type = property_type
            else:
                selected_type = property_types[int(seed[i], 16) % len(property_types)]
                
            # Use location in address if provided
            address_location = location if location else "Example City"
            
            results.append({
                "property_id": property_id,
                "address": f"{100 + int(seed[i:i+2], 16)} {query.title()} St, {address_location}",
                "property_type": selected_type,
                "estimated_value": 100000 + (int(seed[i:i+6], 16) % 900000),
                "source": "mock_data"
            })
            
        return results
    
    async def get_market_data(self, location: str, property_type: str = None) -> Dict[str, Any]:
        """Get market data for a location"""
        # Try to get data from web search first
        if location and settings.BRAVE_API_KEY:
            try:
                web_data = await self.web_search_service.search_market_trends(location, property_type)
                if web_data and "location" in web_data:
                    return web_data
            except Exception as e:
                print(f"Error getting market data from web search: {str(e)}")
        
        # For development, generate mock market data
        seed = hashlib.md5(f"{location}:{property_type or ''}".encode()).hexdigest()
        
        # Generate trends based on seed
        price_trend = (int(seed[0:2], 16) - 128) / 128  # Range: -1.0 to 1.0
        inventory_trend = (int(seed[2:4], 16) - 128) / 128
        days_on_market = max(10, int(seed[4:6], 16) % 90)
        
        return {
            "location": location,
            "property_type": property_type,
            "median_price": 200000 + (int(seed[6:10], 16) % 800000),
            "price_trend_percent": round(price_trend * 10, 1),  # -10% to +10%
            "inventory_trend_percent": round(inventory_trend * 20, 1),  # -20% to +20%
            "average_days_on_market": days_on_market,
            "market_health_index": round(max(1, min(10, 5 + price_trend * 5))),  # 1-10 scale
            "source": "mock_data",
            "timestamp": "2025-03-26T00:00:00Z"
        }
    
    def _get_from_cache(self, property_id: str) -> Optional[Dict[str, Any]]:
        """Get property data from cache"""
        cache_path = os.path.join(settings.OPEN_DATA_CACHE_DIR, f"{property_id}.json")
        if os.path.exists(cache_path):
            try:
                with open(cache_path, 'r') as f:
                    return json.load(f)
            except Exception as e:
                print(f"Error reading from cache: {str(e)}")
        return None
    
    def _save_to_cache(self, property_id: str, data: Dict[str, Any]) -> None:
        """Save property data to cache"""
        cache_path = os.path.join(settings.OPEN_DATA_CACHE_DIR, f"{property_id}.json")
        try:
            with open(cache_path, 'w') as f:
                json.dump(data, f)
        except Exception as e:
            print(f"Error saving to cache: {str(e)}")
    
    async def _get_osm_data(self, osm_id: str) -> Dict[str, Any]:
        """Get property data from OpenStreetMap"""
        if not settings.OPENSTREETMAP_ENABLED:
            return self._generate_mock_data(f"osm-{osm_id}")
            
        url = f"https://nominatim.openstreetmap.org/lookup?osm_ids=N{osm_id}&format=json"
        headers = {
            "User-Agent": "AppraisalAI/1.0"
        }
        
        try:
            response = requests.get(url, headers=headers)
            if response.status_code == 200 and response.json():
                data = response.json()[0]
                return {
                    "property_id": f"osm-{osm_id}",
                    "address": data.get("display_name", ""),
                    "lat": data.get("lat"),
                    "lon": data.get("lon"),
                    "type": data.get("type"),
                    "category": data.get("category"),
                    "source": "openstreetmap"
                }
        except Exception as e:
            print(f"Error fetching OSM data: {str(e)}")
            
        return self._generate_mock_data(f"osm-{osm_id}")
    
    async def _get_geocodio_data(self, address: str) -> Dict[str, Any]:
        """Get property data from Geocodio (has free tier)"""
        if not settings.GEOCODIO_API_KEY:
            return self._generate_mock_data(f"geo-{address}")
            
        url = f"https://api.geocod.io/v1.6/geocode?q={address}&api_key={settings.GEOCODIO_API_KEY}"
        
        try:
            response = requests.get(url)
            if response.status_code == 200:
                data = response.json()
                if data.get("results"):
                    result = data["results"][0]
                    return {
                        "property_id": f"geo-{address}",
                        "address": result.get("formatted_address", address),
                        "lat": result.get("location", {}).get("lat"),
                        "lon": result.get("location", {}).get("lng"),
                        "accuracy": result.get("accuracy"),
                        "accuracy_type": result.get("accuracy_type"),
                        "source": "geocodio"
                    }
        except Exception as e:
            print(f"Error fetching Geocodio data: {str(e)}")
            
        return self._generate_mock_data(f"geo-{address}")
    
    async def _get_attom_data(self, attom_id: str) -> Dict[str, Any]:
        """Get property data from ATTOM (has free tier with limited requests)"""
        if not settings.ATTOM_API_KEY:
            return self._generate_mock_data(f"attom-{attom_id}")
            
        url = f"https://api.gateway.attomdata.com/propertyapi/v1.0.0/property/detail?id={attom_id}"
        headers = {
            "apikey": settings.ATTOM_API_KEY,
            "Accept": "application/json"
        }
        
        try:
            response = requests.get(url, headers=headers)
            if response.status_code == 200:
                data = response.json()
                if data.get("property"):
                    prop = data["property"][0]
                    return {
                        "property_id": f"attom-{attom_id}",
                        "address": f"{prop.get('address', {}).get('line1')} {prop.get('address', {}).get('line2', '')}",
                        "city": prop.get('address', {}).get('city'),
                        "state": prop.get('address', {}).get('state'),
                        "zip": prop.get('address', {}).get('zip'),
                        "lat": prop.get('location', {}).get('latitude'),
                        "lon": prop.get('location', {}).get('longitude'),
                        "property_type": prop.get('summary', {}).get('proptype'),
                        "year_built": prop.get('summary', {}).get('yearbuilt'),
                        "bedrooms": prop.get('building', {}).get('rooms', {}).get('beds'),
                        "bathrooms": prop.get('building', {}).get('rooms', {}).get('bathstotal'),
                        "sqft": prop.get('building', {}).get('size', {}).get('universalsize'),
                        "lot_size": prop.get('lot', {}).get('depth'),
                        "assessed_value": prop.get('assessment', {}).get('assessed', {}).get('assdttlvalue'),
                        "source": "attom"
                    }
        except Exception as e:
            print(f"Error fetching ATTOM data: {str(e)}")
            
        return self._generate_mock_data(f"attom-{attom_id}")
    
    async def _get_web_search_data(self, address: str) -> Dict[str, Any]:
        """Get property data from web search"""
        if not settings.BRAVE_API_KEY:
            return self._generate_mock_data(f"web-{address}")
        
        # Extract city from address if possible
        city = None
        address_parts = address.split(',')
        if len(address_parts) > 1:
            city = address_parts[1].strip()
            address = address_parts[0].strip()
        
        try:
            web_data = await self.web_search_service.search_property_info(address, city)
            if web_data:
                # Add property_id to the data
                web_data["property_id"] = f"web-{address}"
                return web_data
        except Exception as e:
            print(f"Error fetching web search data: {str(e)}")
            
        return self._generate_mock_data(f"web-{address}")
    
    def _generate_mock_data(self, property_id: str) -> Dict[str, Any]:
        """Generate mock property data for development"""
        # Create a hash of the property_id for deterministic results
        hash_val = hashlib.md5(property_id.encode()).hexdigest()
        
        # Use the hash to generate property details
        property_types = ["residential", "commercial", "industrial", "land"]
        property_type = property_types[int(hash_val[0], 16) % len(property_types)]
        
        # Base value between $100,000 and $1,000,000
        base_value = 100000 + (int(hash_val[1:7], 16) % 900000)
        
        # Generate address
        street_number = 100 + (int(hash_val[7:9], 16) % 9000)
        streets = ["Main St", "Oak Ave", "Maple Rd", "Washington Blvd", "Park Lane"]
        street = streets[int(hash_val[9], 16) % len(streets)]
        cities = ["Springfield", "Riverdale", "Oakwood", "Maplewood", "Lakeside"]
        city = cities[int(hash_val[10], 16) % len(cities)]
        
        # Generate property details
        year_built = 1950 + (int(hash_val[11:13], 16) % 70)
        sqft = 1000 + (int(hash_val[13:16], 16) % 5000)
        lot_size = 5000 + (int(hash_val[16:20], 16) % 15000)
        
        # Generate residential-specific details
        bedrooms = 2 + (int(hash_val[20], 16) % 4) if property_type == "residential" else None
        bathrooms = 1 + (int(hash_val[21], 16) % 4) if property_type == "residential" else None
        
        return {
            "property_id": property_id,
            "address": f"{street_number} {street}, {city}",
            "property_type": property_type,
            "sqft": sqft,
            "year_built": year_built,
            "bedrooms": bedrooms,
            "bathrooms": bathrooms,
            "lot_size": lot_size,
            "last_sale_price": base_value,
            "last_sale_date": f"2020-{1 + int(hash_val[22:24], 16) % 12}-{1 + int(hash_val[24:26], 16) % 28}",
            "estimated_value": base_value * (1 + (int(hash_val[26:28], 16) % 50) / 100),
            "source": "mock_data"
        }
