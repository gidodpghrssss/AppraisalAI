"""
Test script to verify the LLM service connection.
"""
import asyncio
import os
from dotenv import load_dotenv
from app.services.llm_service import LLMService, Message

# Load environment variables
load_dotenv()

async def test_llm_connection():
    """Test the LLM service connection."""
    print("Initializing LLM service...")
    llm_service = LLMService()
    
    try:
        print("Testing connection to Nebius API...")
        connection_ok = await llm_service.check_connection()
        print(f"Connection test result: {connection_ok}")
        
        print("\nTesting message generation...")
        messages = [
            Message(role="system", content="You are a helpful assistant."),
            Message(role="user", content="Hello, can you introduce yourself?")
        ]
        
        response = await llm_service.generate_completion(
            messages=messages,
            temperature=0.7,
            max_tokens=100
        )
        
        print("\nResponse from LLM:")
        print(response)
        
        # Extract and print the actual message content
        content = response.get("choices", [{}])[0].get("message", {}).get("content", "")
        print("\nMessage content:")
        print(content)
        
        return True
    except Exception as e:
        print(f"Error: {str(e)}")
        return False

if __name__ == "__main__":
    print("Starting LLM connection test...")
    result = asyncio.run(test_llm_connection())
    
    if result:
        print("\nTest completed successfully!")
    else:
        print("\nTest failed!")
