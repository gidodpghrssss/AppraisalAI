import aiohttp
import json
import re
import hashlib
from typing import List, Dict, Any, Optional
from app.core.config import settings

class WebSearchService:
    """Service for performing web searches to gather property data"""
    
    def __init__(self):
        self.brave_search_url = "https://api.search.brave.com/res/v1/web/search"
        self.headers = {
            "Accept": "application/json",
            "Accept-Encoding": "gzip",
            "X-Subscription-Token": settings.BRAVE_API_KEY
        }
    
    async def search_property_info(self, address: str, city: Optional[str] = None) -> Dict[str, Any]:
        """Search for property information using web search"""
        # Construct search query
        query = f"{address}"
        if city:
            query += f" {city}"
        query += " property details real estate"
        
        search_results = await self._perform_search(query)
        
        # Extract relevant information from search results
        return self._extract_property_info(search_results, address)
    
    async def search_market_trends(self, location: str, property_type: Optional[str] = None) -> Dict[str, Any]:
        """Search for market trends in a specific location"""
        # Construct search query
        query = f"{location} real estate market trends"
        if property_type:
            query += f" {property_type}"
        query += " 2025"
        
        search_results = await self._perform_search(query)
        
        # Extract relevant information from search results
        return self._extract_market_info(search_results, location)
    
    async def _perform_search(self, query: str) -> Dict[str, Any]:
        """Perform a web search using Brave Search API"""
        if not settings.BRAVE_API_KEY:
            # If no API key, return mock results
            return self._generate_mock_search_results(query)
            
        params = {
            "q": query,
            "count": 10,
            "search_lang": "en",
            "safesearch": "moderate"
        }
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(
                    self.brave_search_url,
                    headers=self.headers,
                    params=params
                ) as response:
                    if response.status == 200:
                        return await response.json()
                    else:
                        print(f"Brave search error: {response.status}")
                        return self._generate_mock_search_results(query)
        except Exception as e:
            print(f"Error performing web search: {str(e)}")
            return self._generate_mock_search_results(query)
    
    def _extract_property_info(self, search_results: Dict[str, Any], address: str) -> Dict[str, Any]:
        """Extract property information from search results"""
        # If using mock data, return it directly
        if search_results.get("mock_data"):
            return search_results.get("property_info", {})
            
        # Extract information from real search results
        property_info = {
            "address": address,
            "source": "web_search",
            "listings": []
        }
        
        try:
            # Process web results
            web_results = search_results.get("web", {}).get("results", [])
            
            for result in web_results:
                title = result.get("title", "")
                description = result.get("description", "")
                url = result.get("url", "")
                
                # Check if result is relevant to real estate
                if any(term in title.lower() or term in description.lower() 
                       for term in ["zillow", "redfin", "trulia", "realtor", "property", "home", "house", "real estate"]):
                    
                    # Try to extract price
                    price = self._extract_price(title + " " + description)
                    
                    # Try to extract bedrooms and bathrooms
                    beds, baths = self._extract_beds_baths(title + " " + description)
                    
                    # Try to extract square footage
                    sqft = self._extract_sqft(title + " " + description)
                    
                    property_info["listings"].append({
                        "title": title,
                        "description": description,
                        "url": url,
                        "price": price,
                        "bedrooms": beds,
                        "bathrooms": baths,
                        "sqft": sqft
                    })
            
            # Aggregate information from listings
            if property_info["listings"]:
                # Get the most common price
                prices = [listing.get("price") for listing in property_info["listings"] if listing.get("price")]
                if prices:
                    property_info["estimated_value"] = sum(prices) / len(prices)
                
                # Get the most common beds/baths
                beds = [listing.get("bedrooms") for listing in property_info["listings"] if listing.get("bedrooms")]
                if beds:
                    property_info["bedrooms"] = max(set(beds), key=beds.count)
                
                baths = [listing.get("bathrooms") for listing in property_info["listings"] if listing.get("bathrooms")]
                if baths:
                    property_info["bathrooms"] = max(set(baths), key=baths.count)
                
                # Get the most common sqft
                sqfts = [listing.get("sqft") for listing in property_info["listings"] if listing.get("sqft")]
                if sqfts:
                    property_info["sqft"] = sum(sqfts) / len(sqfts)
        
        except Exception as e:
            print(f"Error extracting property info: {str(e)}")
        
        return property_info
    
    def _extract_market_info(self, search_results: Dict[str, Any], location: str) -> Dict[str, Any]:
        """Extract market trend information from search results"""
        # If using mock data, return it directly
        if search_results.get("mock_data"):
            return search_results.get("market_info", {})
            
        # Extract information from real search results
        market_info = {
            "location": location,
            "source": "web_search",
            "trends": []
        }
        
        try:
            # Process web results
            web_results = search_results.get("web", {}).get("results", [])
            
            for result in web_results:
                title = result.get("title", "")
                description = result.get("description", "")
                url = result.get("url", "")
                
                # Check if result is relevant to market trends
                if any(term in title.lower() or term in description.lower() 
                       for term in ["market trends", "housing market", "real estate market", "property values"]):
                    
                    # Try to extract price trends
                    price_trend = self._extract_percentage(title + " " + description, 
                                                          ["increase", "growth", "appreciation", "rise", "up"],
                                                          ["decrease", "decline", "depreciation", "fall", "down"])
                    
                    # Try to extract inventory trends
                    inventory_trend = self._extract_percentage(title + " " + description, 
                                                             ["inventory increase", "more listings", "more homes"],
                                                             ["inventory decrease", "fewer listings", "fewer homes"])
                    
                    market_info["trends"].append({
                        "title": title,
                        "description": description,
                        "url": url,
                        "price_trend": price_trend,
                        "inventory_trend": inventory_trend
                    })
            
            # Aggregate information from trends
            if market_info["trends"]:
                # Calculate average price trend
                price_trends = [trend.get("price_trend") for trend in market_info["trends"] if trend.get("price_trend") is not None]
                if price_trends:
                    market_info["price_trend_percent"] = sum(price_trends) / len(price_trends)
                
                # Calculate average inventory trend
                inventory_trends = [trend.get("inventory_trend") for trend in market_info["trends"] if trend.get("inventory_trend") is not None]
                if inventory_trends:
                    market_info["inventory_trend_percent"] = sum(inventory_trends) / len(inventory_trends)
                
                # Estimate days on market based on price trends
                if "price_trend_percent" in market_info:
                    price_trend = market_info["price_trend_percent"]
                    # Higher price trends generally mean lower days on market
                    if price_trend > 10:
                        market_info["average_days_on_market"] = 15
                    elif price_trend > 5:
                        market_info["average_days_on_market"] = 30
                    elif price_trend > 0:
                        market_info["average_days_on_market"] = 45
                    elif price_trend > -5:
                        market_info["average_days_on_market"] = 60
                    else:
                        market_info["average_days_on_market"] = 90
                
                # Calculate market health index (1-10 scale)
                if "price_trend_percent" in market_info and "inventory_trend_percent" in market_info:
                    price_trend = market_info["price_trend_percent"]
                    inventory_trend = market_info["inventory_trend_percent"]
                    
                    # Higher price trend and lower inventory trend generally indicate a healthier market
                    market_health = 5 + (price_trend / 4) - (inventory_trend / 8)
                    market_info["market_health_index"] = max(1, min(10, market_health))
        
        except Exception as e:
            print(f"Error extracting market info: {str(e)}")
        
        return market_info
    
    def _extract_price(self, text: str) -> Optional[float]:
        """Extract price from text"""
        # Look for price patterns like $500,000 or $500K
        price_pattern = r'\$\s*(\d{1,3}(?:,\d{3})*(?:\.\d+)?|\d+(?:\.\d+)?)\s*(?:K|k|M|m)?'
        match = re.search(price_pattern, text)
        
        if match:
            price_str = match.group(1).replace(',', '')
            price = float(price_str)
            
            # Check for K or M suffix
            if match.group(0).lower().endswith('k'):
                price *= 1000
            elif match.group(0).lower().endswith('m'):
                price *= 1000000
                
            return price
        
        return None
    
    def _extract_beds_baths(self, text: str) -> tuple:
        """Extract bedrooms and bathrooms from text"""
        # Look for patterns like 3 bed, 2 bath or 3br, 2ba
        beds_pattern = r'(\d+)\s*(?:bed|bedroom|br|bd)'
        baths_pattern = r'(\d+)\s*(?:bath|bathroom|ba)'
        
        beds_match = re.search(beds_pattern, text.lower())
        baths_match = re.search(baths_pattern, text.lower())
        
        beds = int(beds_match.group(1)) if beds_match else None
        baths = int(baths_match.group(1)) if baths_match else None
        
        return beds, baths
    
    def _extract_sqft(self, text: str) -> Optional[float]:
        """Extract square footage from text"""
        # Look for patterns like 1,500 sqft or 1500 sq ft
        sqft_pattern = r'(\d{1,3}(?:,\d{3})*|\d+)\s*(?:sq\.?\s*ft\.?|sqft|square\s*feet)'
        match = re.search(sqft_pattern, text.lower())
        
        if match:
            sqft_str = match.group(1).replace(',', '')
            return float(sqft_str)
        
        return None
    
    def _extract_percentage(self, text: str, positive_terms: List[str], negative_terms: List[str]) -> Optional[float]:
        """Extract percentage change from text"""
        # Look for patterns like "increased by 5.2%" or "5.2% increase"
        percentage_pattern = r'(\d+(?:\.\d+)?)\s*%'
        matches = re.finditer(percentage_pattern, text.lower())
        
        for match in matches:
            percentage = float(match.group(1))
            
            # Check if it's a positive or negative change
            context = text[max(0, match.start() - 50):min(len(text), match.end() + 50)].lower()
            
            is_positive = any(term in context for term in positive_terms)
            is_negative = any(term in context for term in negative_terms)
            
            if is_positive and not is_negative:
                return percentage
            elif is_negative and not is_positive:
                return -percentage
        
        return None
    
    def _generate_mock_search_results(self, query: str) -> Dict[str, Any]:
        """Generate mock search results for development"""
        # Create a hash of the query for deterministic results
        query_hash = hashlib.md5(query.encode()).hexdigest()
        
        # Check if query is for property info or market trends
        is_property_query = "property" in query.lower() or "real estate" in query.lower()
        is_market_query = "market" in query.lower() or "trends" in query.lower()
        
        if is_property_query:
            # Extract address from query
            address = query.split(" property")[0].strip()
            
            # Generate mock property info
            property_info = {
                "address": address,
                "estimated_value": 100000 + (int(query_hash[0:6], 16) % 900000),
                "bedrooms": 2 + (int(query_hash[6], 16) % 4),
                "bathrooms": 1 + (int(query_hash[7], 16) % 4),
                "sqft": 1000 + (int(query_hash[8:11], 16) % 3000),
                "year_built": 1950 + (int(query_hash[11:13], 16) % 70),
                "source": "web_search_mock"
            }
            
            return {
                "mock_data": True,
                "property_info": property_info
            }
            
        elif is_market_query:
            # Extract location from query
            location = query.split(" real estate")[0].strip()
            
            # Generate mock market info
            price_trend = (int(query_hash[0:2], 16) - 128) / 12.8  # Range: -10.0 to 10.0
            inventory_trend = (int(query_hash[2:4], 16) - 128) / 6.4  # Range: -20.0 to 20.0
            
            market_info = {
                "location": location,
                "price_trend_percent": round(price_trend, 1),
                "inventory_trend_percent": round(inventory_trend, 1),
                "average_days_on_market": 20 + (int(query_hash[4:6], 16) % 70),
                "market_health_index": 1 + (int(query_hash[6], 16) % 10),
                "source": "web_search_mock"
            }
            
            return {
                "mock_data": True,
                "market_info": market_info
            }
            
        else:
            # Generic mock search results
            return {
                "mock_data": True,
                "web": {
                    "results": [
                        {
                            "title": f"Mock Result 1 for {query}",
                            "description": "This is a mock search result for development purposes.",
                            "url": "https://example.com/1"
                        },
                        {
                            "title": f"Mock Result 2 for {query}",
                            "description": "This is another mock search result for development purposes.",
                            "url": "https://example.com/2"
                        }
                    ]
                }
            }
