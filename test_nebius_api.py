"""
Test script to diagnose Nebius API connection issues.
"""
import os
import json
import httpx
import asyncio
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

async def test_api_endpoints():
    """Test different variations of the Nebius API endpoint to find the correct one."""
    api_key = os.getenv("NEBIUS_API_KEY")
    model = os.getenv("MODEL_NAME", "Llama-3.1-70B-Instruct")
    
    # List of possible endpoint formats to try based on Nebius documentation
    endpoints = [
        "https://api.studio.nebius.com/v1/chat/completions",
        "https://api.studio.nebius.com/v1/completions",
        "https://llm.api.nebius.cloud/v1/chat/completions",
        "https://llm.api.nebius.cloud/v1/completions"
    ]
    
    # Different model name formats to try
    model_names = [
        "Llama-3.1-70B-Instruct",
        "meta-llama/Meta-Llama-3.1-70B-Instruct",
        "meta-llama/Llama-3.1-70B-Instruct"
    ]
    
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {api_key}"  # Try Bearer token format
    }
    
    headers_api_key = {
        "Content-Type": "application/json",
        "Authorization": f"Api-Key {api_key}"  # Try Api-Key format
    }
    
    test_message = [
        {"role": "system", "content": "You are a helpful assistant."},
        {"role": "user", "content": "Hello"}
    ]
    
    print(f"Testing Nebius API with API key (first 10 chars): {api_key[:10]}...")
    
    # Test all combinations of endpoints, model names, and header formats
    for endpoint in endpoints:
        for model_name in model_names:
            for header in [headers, headers_api_key]:
                auth_type = "Bearer token" if "Bearer" in header["Authorization"] else "Api-Key"
                print(f"\nTesting endpoint: {endpoint}")
                print(f"Model name: {model_name}")
                print(f"Auth type: {auth_type}")
                
                payload = {
                    "model": model_name,
                    "messages": test_message,
                    "temperature": 0.7,
                    "max_tokens": 10
                }
                
                try:
                    async with httpx.AsyncClient(timeout=15.0) as client:
                        response = await client.post(
                            endpoint,
                            headers=header,
                            json=payload
                        )
                        
                        print(f"Status code: {response.status_code}")
                        if response.status_code == 200:
                            print("SUCCESS! Endpoint is working.")
                            print("Response:")
                            print(json.dumps(response.json(), indent=2))
                            print("\nThis is the correct configuration to use.")
                            return {
                                "endpoint": endpoint,
                                "model_name": model_name,
                                "auth_type": auth_type
                            }
                        else:
                            print(f"Error response: {response.text}")
                except Exception as e:
                    print(f"Connection error: {str(e)}")
    
    print("\nNone of the tested configurations worked.")
    return None

if __name__ == "__main__":
    print("Starting Nebius API endpoint test...")
    working_config = asyncio.run(test_api_endpoints())
    
    if working_config:
        print(f"\nWorking configuration found:")
        print(f"Endpoint: {working_config['endpoint']}")
        print(f"Model name: {working_config['model_name']}")
        print(f"Auth type: {working_config['auth_type']}")
        print("\nUpdate your .env file with this configuration:")
        print(f"NEBIUS_ENDPOINT={working_config['endpoint']}")
        print(f"MODEL_NAME={working_config['model_name']}")
    else:
        print("\nNo working configuration found. Please check your API key and model name.")
        print("You may need to contact Nebius support for the correct endpoint information.")
