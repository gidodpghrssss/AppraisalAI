"""
LLM service for interacting with Nebius API to access language models.
"""
import json
import logging
from typing import Dict, List, Any, Optional
from pydantic import BaseModel
from openai import OpenAI

from app.core.config import settings

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class Message(BaseModel):
    """Message model for LLM conversations."""
    role: str
    content: str

class LLMService:
    """Service for interacting with Nebius LLM API using OpenAI client."""
    
    def __init__(self):
        """Initialize the LLM service."""
        self.api_key = settings.NEBIUS_API_KEY
        self.base_url = settings.NEBIUS_ENDPOINT.rsplit("/chat/completions", 1)[0]
        self.model = settings.MODEL_NAME
        
        # Initialize OpenAI client with Nebius configuration
        self.client = OpenAI(
            api_key=self.api_key,
            base_url=self.base_url
        )
        
        logger.info(f"Initialized LLM service with model: {self.model}")
        logger.info(f"Using base URL: {self.base_url}")
    
    async def check_connection(self) -> bool:
        """
        Check if the connection to the LLM API is working.
        Returns True if connection is successful, False otherwise.
        """
        # Simple test query to check if the API is responsive
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are a helpful assistant."},
                    {"role": "user", "content": "Hello"}
                ],
                max_tokens=10
            )
            logger.info("LLM API connection successful")
            return True
        except Exception as e:
            logger.error(f"Error connecting to LLM API: {str(e)}")
            return False
    
    async def generate_completion(
        self, 
        messages: List[Message], 
        temperature: float = 0.7,
        max_tokens: int = 1024,
        tools: Optional[List[Dict[str, Any]]] = None
    ) -> Dict[str, Any]:
        """
        Generate a completion from the LLM.
        
        Args:
            messages: List of messages in the conversation
            temperature: Temperature for generation (0.0 to 1.0)
            max_tokens: Maximum number of tokens to generate
            tools: Optional list of tools to provide to the model
            
        Returns:
            The LLM response
        """
        # Convert Message objects to dict format expected by API
        formatted_messages = [{"role": msg.role, "content": msg.content} for msg in messages]
        
        try:
            # Create completion request
            if tools:
                response = self.client.chat.completions.create(
                    model=self.model,
                    messages=formatted_messages,
                    temperature=temperature,
                    max_tokens=max_tokens,
                    tools=tools
                )
            else:
                response = self.client.chat.completions.create(
                    model=self.model,
                    messages=formatted_messages,
                    temperature=temperature,
                    max_tokens=max_tokens
                )
            
            # Convert response to dictionary
            return response.model_dump()
            
        except Exception as e:
            logger.error(f"Exception during LLM API call: {str(e)}")
            return {"error": "Exception during API call", "details": str(e)}
    
    async def generate_with_tools(
        self,
        messages: List[Message],
        tools: List[Dict[str, Any]],
        temperature: float = 0.7,
        max_tokens: int = 1024
    ) -> Dict[str, Any]:
        """
        Generate a completion with tool calling capabilities.
        
        Args:
            messages: List of messages in the conversation
            tools: List of tools to provide to the model
            temperature: Temperature for generation
            max_tokens: Maximum number of tokens to generate
            
        Returns:
            The LLM response with tool calls
        """
        return await self.generate_completion(
            messages=messages,
            temperature=temperature,
            max_tokens=max_tokens,
            tools=tools
        )

# Alias for backward compatibility
LlamaService = LLMService
