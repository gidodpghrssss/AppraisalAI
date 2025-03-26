from typing import Dict, Any, List, Optional
from pydantic import BaseModel
from app.services.property_data_service import PropertyDataService
from app.services.web_search_service import WebSearchService
from app.core.config import settings

class PropertyInput(BaseModel):
    property_id: Optional[str] = None
    address: Optional[str] = None
    location: Optional[str] = None
    property_type: Optional[str] = None

class PropertyAnalysisTool:
    """Tool for analyzing property data using free data sources"""
    
    def __init__(self):
        self.property_data_service = PropertyDataService()
        self.web_search_service = WebSearchService()
    
    async def analyze_property(self, property_input: PropertyInput) -> Dict[str, Any]:
        """Analyze a property using available data sources"""
        # Get property data
        if property_input.property_id:
            property_data = await self.property_data_service.get_property_data(property_input.property_id)
        elif property_input.address:
            # Convert address to a property ID for the geocodio service
            property_id = f"geo-{property_input.address}"
            property_data = await self.property_data_service.get_property_data(property_id)
        else:
            # Search for properties if we only have location
            search_results = await self.property_data_service.search_properties(
                query=property_input.location or "Example", 
                location=property_input.location,
                property_type=property_input.property_type
            )
            if search_results:
                property_data = await self.property_data_service.get_property_data(search_results[0]["property_id"])
            else:
                # Try web search if property not found in regular sources
                if settings.BRAVE_API_KEY:
                    try:
                        web_data = await self.web_search_service.search_property_info(
                            property_input.address,
                            property_input.location
                        )
                        if web_data:
                            property_data = web_data
                        else:
                            property_data = self._generate_empty_property_data()
                    except Exception as e:
                        print(f"Error searching with web search: {str(e)}")
                        property_data = self._generate_empty_property_data()
                else:
                    property_data = self._generate_empty_property_data()
        
        # Get market data for the property's location
        location = property_data.get("city", property_input.location or "Unknown")
        market_data = await self.property_data_service.get_market_data(
            location=location,
            property_type=property_data.get("property_type", property_input.property_type)
        )
        
        # Combine data for analysis
        analysis_data = {
            "property": property_data,
            "market": market_data,
            "analysis": {}
        }
        
        # Perform valuation analysis
        analysis_data["analysis"] = self._analyze_property_value(property_data, market_data)
        
        return analysis_data
    
    def _analyze_property_value(self, property_data: Dict[str, Any], market_data: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze property value based on property and market data"""
        # Extract property details
        estimated_value = property_data.get("estimated_value", 0)
        last_sale_price = property_data.get("last_sale_price", 0)
        last_sale_date = property_data.get("last_sale_date")
        
        # Extract market details
        median_price = market_data.get("median_price", 0)
        price_trend_percent = market_data.get("price_trend_percent", 0)
        
        # Calculate years since last sale
        years_since_sale = 0
        if last_sale_date:
            try:
                sale_date = datetime.strptime(last_sale_date, "%Y-%m-%d")
                years_since_sale = (datetime.now() - sale_date).days / 365
            except:
                years_since_sale = 3  # Default if date parsing fails
        
        # Calculate appreciation since last sale
        if last_sale_price and last_sale_price > 0:
            appreciation = ((estimated_value - last_sale_price) / last_sale_price) * 100
            annual_appreciation = appreciation / max(1, years_since_sale)
        else:
            appreciation = 0
            annual_appreciation = 0
            
        # Calculate market comparison
        if median_price and median_price > 0:
            market_ratio = (estimated_value / median_price) * 100
        else:
            market_ratio = 100
            
        # Calculate future value projection
        future_value_1yr = estimated_value * (1 + (price_trend_percent / 100))
        future_value_5yr = estimated_value * (1 + (price_trend_percent / 100)) ** 5
        
        # Generate investment metrics
        cap_rate = self._calculate_cap_rate(property_data)
        cash_on_cash = self._calculate_cash_on_cash(property_data)
        
        # Generate risk assessment
        risk_score = self._calculate_risk_score(property_data, market_data)
        
        return {
            "estimated_value": round(estimated_value, 2),
            "confidence_score": self._calculate_confidence_score(property_data),
            "value_factors": self._identify_value_factors(property_data),
            "appreciation": {
                "since_last_sale_percent": round(appreciation, 2),
                "annual_percent": round(annual_appreciation, 2),
                "market_comparison_percent": round(market_ratio - 100, 2)
            },
            "future_projection": {
                "value_1yr": round(future_value_1yr, 2),
                "value_5yr": round(future_value_5yr, 2)
            },
            "investment_metrics": {
                "cap_rate_percent": round(cap_rate, 2),
                "cash_on_cash_percent": round(cash_on_cash, 2),
                "price_to_rent_ratio": self._calculate_price_to_rent(property_data)
            },
            "risk_assessment": {
                "overall_risk_score": risk_score,
                "risk_factors": self._identify_risk_factors(property_data, market_data)
            },
            "comparable_properties": self._generate_comps(property_data, market_data),
            "web_search_insights": self._extract_web_search_insights(property_data)
        }
    
    def _calculate_confidence_score(self, property_data: Dict[str, Any]) -> float:
        """Calculate confidence score for the valuation"""
        # Base confidence based on data source
        source = property_data.get("source", "")
        if source == "attom":
            base_confidence = 0.9
        elif source == "web_search":
            base_confidence = 0.75
        elif source == "openstreetmap":
            base_confidence = 0.6
        elif source == "geocodio":
            base_confidence = 0.65
        else:
            base_confidence = 0.5
            
        # Adjust based on data completeness
        key_fields = ["address", "property_type", "sqft", "bedrooms", "bathrooms", "year_built", "lot_size"]
        completeness = sum(1 for field in key_fields if property_data.get(field)) / len(key_fields)
        
        # Calculate final score (0-100)
        confidence_score = (base_confidence * 0.7 + completeness * 0.3) * 100
        return min(95, round(confidence_score, 0))  # Cap at 95
    
    def _identify_value_factors(self, property_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Identify factors affecting property value"""
        factors = []
        
        # Check property size
        sqft = property_data.get("sqft")
        if sqft and sqft > 2500:
            factors.append({
                "factor": "Large living area",
                "impact": "positive",
                "description": f"Property size of {sqft} sqft is above average"
            })
        elif sqft and sqft < 1000:
            factors.append({
                "factor": "Small living area",
                "impact": "negative",
                "description": f"Property size of {sqft} sqft is below average"
            })
            
        # Check property age
        year_built = property_data.get("year_built")
        current_year = datetime.now().year
        if year_built and (current_year - year_built) < 10:
            factors.append({
                "factor": "New construction",
                "impact": "positive",
                "description": f"Built in {year_built}, property is relatively new"
            })
        elif year_built and (current_year - year_built) > 50:
            factors.append({
                "factor": "Older property",
                "impact": "negative",
                "description": f"Built in {year_built}, may require more maintenance"
            })
            
        # Check lot size
        lot_size = property_data.get("lot_size")
        if lot_size and lot_size > 10000:
            factors.append({
                "factor": "Large lot",
                "impact": "positive",
                "description": f"Lot size of {lot_size} sqft is above average"
            })
            
        # Check property type
        property_type = property_data.get("property_type", "").lower()
        if property_type == "residential":
            # Check bed/bath ratio
            beds = property_data.get("bedrooms")
            baths = property_data.get("bathrooms")
            if beds and baths and beds > 0:
                ratio = baths / beds
                if ratio >= 1.5:
                    factors.append({
                        "factor": "High bath-to-bed ratio",
                        "impact": "positive",
                        "description": f"{baths} bathrooms for {beds} bedrooms is above average"
                    })
        
        # Add web search factors if available
        if property_data.get("source") == "web_search" and property_data.get("listings"):
            factors.append({
                "factor": "Multiple online listings",
                "impact": "neutral",
                "description": f"Property has {len(property_data['listings'])} online listings"
            })
            
        return factors
    
    def _calculate_cap_rate(self, property_data: Dict[str, Any]) -> float:
        """Calculate capitalization rate"""
        # For development, generate a realistic cap rate
        property_type = property_data.get("property_type", "").lower()
        estimated_value = property_data.get("estimated_value", 200000)
        
        if property_type == "residential":
            # Typical residential cap rates: 4-10%
            base_rate = 6.0
        elif property_type == "commercial":
            # Typical commercial cap rates: 5-12%
            base_rate = 8.0
        elif property_type == "industrial":
            # Typical industrial cap rates: 6-12%
            base_rate = 9.0
        else:
            base_rate = 7.0
            
        # Adjust based on property value (higher value properties typically have lower cap rates)
        value_factor = max(0.5, min(1.5, 1000000 / max(100000, estimated_value)))
        
        # Add some variability
        seed = hashlib.md5(str(estimated_value).encode()).hexdigest()
        variability = (int(seed[0:2], 16) - 128) / 256  # -0.5 to 0.5
        
        return base_rate * value_factor + variability
    
    def _calculate_cash_on_cash(self, property_data: Dict[str, Any]) -> float:
        """Calculate cash-on-cash return"""
        # For development, base on cap rate with adjustments
        cap_rate = self._calculate_cap_rate(property_data)
        
        # Cash-on-cash is typically higher than cap rate due to leverage
        leverage_factor = 1.5
        
        # Add variability
        seed = hashlib.md5(str(property_data.get("estimated_value", 0)).encode()).hexdigest()
        variability = (int(seed[2:4], 16) - 128) / 256  # -0.5 to 0.5
        
        return cap_rate * leverage_factor + variability
    
    def _calculate_price_to_rent(self, property_data: Dict[str, Any]) -> float:
        """Calculate price-to-rent ratio"""
        estimated_value = property_data.get("estimated_value", 200000)
        property_type = property_data.get("property_type", "").lower()
        
        # Estimate monthly rent
        if property_type == "residential":
            # Typical price-to-rent ratios range from 15-20
            base_ratio = 17
        elif property_type == "commercial":
            # Commercial properties typically have lower ratios
            base_ratio = 12
        else:
            base_ratio = 15
            
        # Add variability
        seed = hashlib.md5(str(estimated_value).encode()).hexdigest()
        variability = (int(seed[4:6], 16) - 128) / 128  # -1.0 to 1.0
        
        return base_ratio + variability
    
    def _calculate_risk_score(self, property_data: Dict[str, Any], market_data: Dict[str, Any]) -> int:
        """Calculate risk score (1-10, where 1 is lowest risk)"""
        # Start with a base risk
        base_risk = 5
        
        # Adjust for property type
        property_type = property_data.get("property_type", "").lower()
        if property_type == "residential":
            type_risk = -1  # Lower risk
        elif property_type == "commercial":
            type_risk = 1  # Higher risk
        elif property_type == "industrial":
            type_risk = 2  # Higher risk
        else:
            type_risk = 0
            
        # Adjust for property age
        year_built = property_data.get("year_built")
        if year_built:
            age = datetime.now().year - year_built
            if age < 5:
                age_risk = -1  # Newer is lower risk
            elif age > 30:
                age_risk = 1  # Older is higher risk
            else:
                age_risk = 0
        else:
            age_risk = 0
            
        # Adjust for market trends
        price_trend = market_data.get("price_trend_percent", 0)
        if price_trend > 5:
            market_risk = -1  # Strong appreciation lowers risk
        elif price_trend < -5:
            market_risk = 2  # Depreciation increases risk
        else:
            market_risk = 0
            
        # Adjust for data source reliability
        source = property_data.get("source", "")
        if source == "attom":
            source_risk = -1  # More reliable data
        elif source == "web_search":
            source_risk = 0  # Moderate reliability
        elif source == "mock_data":
            source_risk = 1  # Less reliable
        else:
            source_risk = 0
            
        # Calculate final risk score
        risk_score = base_risk + type_risk + age_risk + market_risk + source_risk
        
        # Ensure within bounds
        return max(1, min(10, risk_score))
    
    def _identify_risk_factors(self, property_data: Dict[str, Any], market_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Identify risk factors for the property"""
        risk_factors = []
        
        # Check property age
        year_built = property_data.get("year_built")
        if year_built and (datetime.now().year - year_built) > 30:
            risk_factors.append({
                "factor": "Property age",
                "risk_level": "medium",
                "description": f"Built in {year_built}, may require significant maintenance"
            })
            
        # Check market trends
        price_trend = market_data.get("price_trend_percent", 0)
        if price_trend < -2:
            risk_factors.append({
                "factor": "Market depreciation",
                "risk_level": "high",
                "description": f"Market showing {price_trend}% price trend"
            })
        elif price_trend < 0:
            risk_factors.append({
                "factor": "Market stagnation",
                "risk_level": "medium",
                "description": f"Market showing {price_trend}% price trend"
            })
            
        # Check days on market
        days_on_market = market_data.get("average_days_on_market", 0)
        if days_on_market > 60:
            risk_factors.append({
                "factor": "Extended market time",
                "risk_level": "medium",
                "description": f"Average {days_on_market} days on market indicates slow sales"
            })
            
        # Check data reliability
        source = property_data.get("source", "")
        if source == "mock_data":
            risk_factors.append({
                "factor": "Limited data",
                "risk_level": "medium",
                "description": "Analysis based on limited or estimated data"
            })
            
        # Check property type risks
        property_type = property_data.get("property_type", "").lower()
        if property_type == "commercial" or property_type == "industrial":
            risk_factors.append({
                "factor": f"{property_type.title()} property type",
                "risk_level": "medium",
                "description": f"{property_type.title()} properties typically have higher market volatility"
            })
            
        return risk_factors
    
    def _generate_comps(self, property_data: Dict[str, Any], market_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Generate comparable properties"""
        # For development, generate mock comparable properties
        comps = []
        
        # Use property data to generate realistic comps
        base_value = property_data.get("estimated_value", 200000)
        property_type = property_data.get("property_type", "unknown")
        sqft = property_data.get("sqft", 1500)
        beds = property_data.get("bedrooms", 3)
        baths = property_data.get("bathrooms", 2)
        
        # Generate 3 comparable properties
        for i in range(3):
            # Create a hash for deterministic but varied results
            seed = hashlib.md5(f"{property_data.get('property_id', '')}-comp-{i}".encode()).hexdigest()
            
            # Vary the price by ±10%
            price_var = (int(seed[0:4], 16) - 32768) / 32768  # -1.0 to 1.0
            comp_price = base_value * (1 + (price_var * 0.1))
            
            # Vary the square footage by ±15%
            sqft_var = (int(seed[4:8], 16) - 32768) / 32768  # -1.0 to 1.0
            comp_sqft = max(500, int(sqft * (1 + (sqft_var * 0.15))))
            
            # Vary beds/baths slightly
            bed_var = int(seed[8], 16) % 3 - 1  # -1, 0, or 1
            bath_var = int(seed[9], 16) % 3 - 1  # -1, 0, or 1
            comp_beds = max(1, beds + bed_var)
            comp_baths = max(1, baths + bath_var)
            
            # Generate an address
            streets = ["Oak", "Maple", "Pine", "Cedar", "Elm"]
            street_types = ["St", "Ave", "Blvd", "Dr", "Ln"]
            street = streets[int(seed[10], 16) % len(streets)]
            street_type = street_types[int(seed[11], 16) % len(street_types)]
            street_num = 100 + (int(seed[12:15], 16) % 9000)
            
            # Extract city from market data or property data
            city = market_data.get("location", "")
            if not city and "address" in property_data:
                address_parts = property_data["address"].split(",")
                if len(address_parts) > 1:
                    city = address_parts[1].strip()
            
            comps.append({
                "address": f"{street_num} {street} {street_type}, {city}",
                "property_type": property_type,
                "price": round(comp_price, 2),
                "sqft": comp_sqft,
                "price_per_sqft": round(comp_price / comp_sqft, 2),
                "bedrooms": comp_beds,
                "bathrooms": comp_baths,
                "year_built": property_data.get("year_built", 2000) + (int(seed[15], 16) % 10 - 5),
                "distance_miles": round((int(seed[16:18], 16) % 20) / 10, 1),
                "source": "comparable_analysis"
            })
            
        return comps
    
    def _extract_web_search_insights(self, property_data: Dict[str, Any]) -> Dict[str, Any]:
        """Extract insights from web search data if available"""
        if property_data.get("source") != "web_search" or not property_data.get("listings"):
            return {}
            
        insights = {
            "listing_count": len(property_data.get("listings", [])),
            "sources": [],
            "key_features": [],
            "market_mentions": []
        }
        
        # Extract unique sources
        sources = set()
        for listing in property_data.get("listings", []):
            if "url" in listing:
                domain = listing["url"].split("//")[-1].split("/")[0]
                sources.add(domain)
                
        insights["sources"] = list(sources)
        
        # Extract key features from descriptions
        feature_keywords = ["renovated", "updated", "new", "modern", "spacious", 
                           "garage", "pool", "view", "granite", "stainless"]
        
        feature_counts = {keyword: 0 for keyword in feature_keywords}
        
        for listing in property_data.get("listings", []):
            description = listing.get("description", "").lower()
            for keyword in feature_keywords:
                if keyword in description:
                    feature_counts[keyword] += 1
                    
        # Add features mentioned in multiple listings
        for keyword, count in feature_counts.items():
            if count > 1:
                insights["key_features"].append({
                    "feature": keyword,
                    "mention_count": count
                })
                
        # Extract market mentions
        market_keywords = ["hot market", "seller's market", "buyer's market", 
                          "competitive", "fast selling", "appreciating"]
        
        market_counts = {keyword: 0 for keyword in market_keywords}
        
        for listing in property_data.get("listings", []):
            description = listing.get("description", "").lower()
            for keyword in market_keywords:
                if keyword in description:
                    market_counts[keyword] += 1
                    
        # Add market terms mentioned
        for keyword, count in market_counts.items():
            if count > 0:
                insights["market_mentions"].append({
                    "term": keyword,
                    "mention_count": count
                })
                
        return insights
    
    def _generate_empty_property_data(self) -> Dict[str, Any]:
        """Generate empty property data when no property is found"""
        return {
            "property_id": "unknown",
            "address": "Unknown Address",
            "property_type": "unknown",
            "sqft": 0,
            "year_built": 0,
            "estimated_value": 0,
            "source": "none"
        }
