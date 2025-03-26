from llama_stack import Tool, Agent
from typing import Dict, Any, List
from app.services.llm_service import LlamaService
from app.tools.property_analysis import PropertyAnalysisTool

class AppraisalAgent(Agent):
    def __init__(self):
        super().__init__(
            name="appraisal_agent",
            description="AI Agent for real estate appraisal and analysis"
        )
        self.llm_service = LlamaService()
        
        # Register tools
        self.tools = [
            PropertyAnalysisTool(),
            Tool(
                name="market_analysis",
                description="Analyze market conditions and trends",
                function=self.analyze_market
            ),
            Tool(
                name="value_estimation",
                description="Estimate property value based on various factors",
                function=self.estimate_value
            ),
            Tool(
                name="risk_assessment",
                description="Assess property and investment risks",
                function=self.assess_risks
            )
        ]

    async def analyze_market(self, location: str, property_type: str) -> Dict[str, Any]:
        """Analyze market conditions for a specific location and property type"""
        return await self.llm_service.get_market_insights(location, property_type)

    async def estimate_value(self, property_details: Dict[str, Any]) -> Dict[str, Any]:
        """Estimate property value based on provided details"""
        analysis = await self.llm_service.analyze_property(
            property_details,
            analysis_type="valuation"
        )
        return {
            "property_id": property_details.get("property_id"),
            "estimated_value": analysis.get("analysis"),
            "confidence_score": 0.85  # This would be calculated based on data quality
        }

    async def assess_risks(self, property_details: Dict[str, Any]) -> Dict[str, Any]:
        """Assess property and investment risks"""
        analysis = await self.llm_service.analyze_property(
            property_details,
            analysis_type="risk"
        )
        return {
            "property_id": property_details.get("property_id"),
            "risk_analysis": analysis.get("analysis")
        }

    async def process_request(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """Process an appraisal request"""
        # Determine which tools to use based on request type
        if request.get("type") == "market_analysis":
            market_data = await self.analyze_market(
                request.get("location"),
                request.get("property_type")
            )
            return market_data
            
        elif request.get("type") == "full_appraisal":
            # Run multiple tools in sequence
            market_data = await self.analyze_market(
                request.get("location"),
                request.get("property_type")
            )
            
            value_estimate = await self.estimate_value(
                request.get("property_details")
            )
            
            risk_assessment = await self.assess_risks(
                request.get("property_details")
            )
            
            return {
                "market_analysis": market_data,
                "value_estimate": value_estimate,
                "risk_assessment": risk_assessment,
                "property_id": request.get("property_details", {}).get("property_id")
            }
        
        else:
            raise ValueError(f"Unknown request type: {request.get('type')}")

    def get_system_prompt(self) -> str:
        """Get the system prompt for the agent"""
        return """You are an expert real estate appraisal AI agent. 
        Your role is to:
        1. Analyze property details and market conditions
        2. Estimate property values
        3. Assess investment risks
        4. Provide comprehensive appraisal reports
        
        Use available tools to gather data and perform analysis.
        Always provide clear explanations for your conclusions."""
