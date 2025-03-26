from openai import OpenAI
from typing import List, Dict, Any
import os
from app.core.config import settings
from llama_stack import LlamaStack

class LlamaService:
    def __init__(self):
        # Initialize OpenAI client with Nebius API
        self.client = OpenAI(
            base_url=settings.NEBIUS_API_URL,
            api_key=settings.NEBIUS_API_KEY
        )
        self.model = "meta-llama/Meta-Llama-3.1-405B-Instruct"
        
        # Initialize LlamaStack for more advanced agent capabilities
        self.llama_stack = LlamaStack(
            api_key=settings.NEBIUS_API_KEY,
            api_url=settings.NEBIUS_API_URL,
            model_name=self.model
        )

    async def get_completion(self, messages: List[Dict[str, str]], temperature: float = 0.7) -> str:
        """
        Get completion from Llama model through Nebius API
        """
        try:
            completion = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=temperature
            )
            return completion.choices[0].message.content
        except Exception as e:
            print(f"Error getting completion: {str(e)}")
            raise

    async def analyze_property(self, 
                             property_details: Dict[str, Any],
                             analysis_type: str = "full") -> Dict[str, Any]:
        """
        Analyze property using Llama model
        """
        system_prompt = """You are an expert real estate appraiser AI assistant. 
        Analyze the provided property details and provide a comprehensive evaluation.
        Focus on key factors that affect property value."""

        property_prompt = f"""
        Property Details: {property_details}
        Analysis Type: {analysis_type}
        
        Provide a detailed analysis including:
        1. Market value estimation
        2. Key value factors
        3. Risk assessment
        4. Comparable properties considerations
        5. Recommendations
        """

        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": property_prompt}
        ]

        analysis = await self.get_completion(messages)
        return {
            "analysis": analysis,
            "property_id": property_details.get("property_id"),
            "analysis_type": analysis_type
        }

    async def get_market_insights(self, location: str, property_type: str) -> Dict[str, Any]:
        """
        Get market insights for a specific location and property type
        """
        prompt = f"""Analyze the real estate market for:
        Location: {location}
        Property Type: {property_type}
        
        Provide insights on:
        1. Market trends
        2. Price movements
        3. Supply and demand
        4. Investment potential
        5. Risk factors
        """

        messages = [
            {"role": "system", "content": "You are a real estate market analysis expert."},
            {"role": "user", "content": prompt}
        ]

        insights = await self.get_completion(messages)
        return {
            "location": location,
            "property_type": property_type,
            "insights": insights
        }
