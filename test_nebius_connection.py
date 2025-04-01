"""
Comprehensive Nebius API Connection Tester

This script performs a series of tests to diagnose and troubleshoot
connection issues with the Nebius API for the Llama-3.1-70B-Instruct model.
It tests different authentication methods, endpoints, and model names.

Usage:
    python test_nebius_connection.py
"""
import os
import json
import asyncio
import httpx
from dotenv import load_dotenv
from rich.console import Console
from rich.table import Table

# Load environment variables
load_dotenv()

# Initialize console for pretty output
console = Console()

# Configuration
API_KEY = os.getenv("NEBIUS_API_KEY", "")
ENDPOINTS = [
    "https://api.studio.nebius.com/v1/chat/completions",
    "https://api.studio.nebius.com/v1/completions",
    "https://llm.api.nebius.cloud/v1/completion",
    "https://llm.api.nebius.cloud/v1/chat/completions"
]
MODEL_NAMES = [
    "meta-llama/Meta-Llama-3.1-70B-Instruct",
    "Meta-Llama-3.1-70B-Instruct",
    "llama-3.1-70b-instruct",
    "meta-llama/llama-3.1-70b-instruct"
]
AUTH_METHODS = [
    {"type": "Bearer", "header": {"Authorization": f"Bearer {API_KEY}"}},
    {"type": "Api-Key", "header": {"Api-Key": API_KEY}}
]

async def test_endpoint(endpoint, model_name, auth_method):
    """Test a specific combination of endpoint, model name, and auth method."""
    headers = {
        "Content-Type": "application/json",
        **auth_method["header"]
    }
    
    # Determine if we're using a chat completion or regular completion endpoint
    is_chat_endpoint = "chat/completions" in endpoint
    
    if is_chat_endpoint:
        payload = {
            "model": model_name,
            "messages": [
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": "Hello, who are you?"}
            ],
            "temperature": 0.7,
            "max_tokens": 100
        }
    else:
        payload = {
            "model": model_name,
            "prompt": "Hello, who are you?",
            "temperature": 0.7,
            "max_tokens": 100
        }
    
    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(
                endpoint,
                headers=headers,
                json=payload
            )
            
            status_code = response.status_code
            
            if status_code == 200:
                result = "✅ SUCCESS"
                response_json = response.json()
                content = ""
                
                if is_chat_endpoint:
                    if "choices" in response_json and len(response_json["choices"]) > 0:
                        message = response_json["choices"][0].get("message", {})
                        content = message.get("content", "")
                else:
                    if "choices" in response_json and len(response_json["choices"]) > 0:
                        content = response_json["choices"][0].get("text", "")
                
                # Truncate content for display
                content_preview = content[:50] + "..." if content and len(content) > 50 else content
                
                return {
                    "endpoint": endpoint,
                    "model": model_name,
                    "auth": auth_method["type"],
                    "status": status_code,
                    "result": result,
                    "content_preview": content_preview,
                    "response": response_json
                }
            else:
                error_detail = ""
                try:
                    error_json = response.json()
                    error_detail = json.dumps(error_json, indent=2)
                except:
                    error_detail = response.text
                
                return {
                    "endpoint": endpoint,
                    "model": model_name,
                    "auth": auth_method["type"],
                    "status": status_code,
                    "result": f"❌ ERROR ({status_code})",
                    "content_preview": error_detail[:100] + "..." if len(error_detail) > 100 else error_detail,
                    "response": error_detail
                }
                
    except Exception as e:
        return {
            "endpoint": endpoint,
            "model": model_name,
            "auth": auth_method["type"],
            "status": "Exception",
            "result": f"❌ EXCEPTION",
            "content_preview": str(e)[:100] + "..." if len(str(e)) > 100 else str(e),
            "response": str(e)
        }

async def run_tests():
    """Run all test combinations and display results."""
    console.print("[bold green]Starting Nebius API Connection Tests[/bold green]")
    console.print(f"API Key: {'✅ Set' if API_KEY else '❌ Not Set'}")
    
    if not API_KEY:
        console.print("[bold red]ERROR: No API key found. Please set the NEBIUS_API_KEY environment variable.[/bold red]")
        return
    
    # Create results table
    table = Table(title="Nebius API Connection Test Results")
    table.add_column("Endpoint", style="cyan")
    table.add_column("Model", style="green")
    table.add_column("Auth", style="yellow")
    table.add_column("Status", style="blue")
    table.add_column("Result", style="magenta")
    table.add_column("Response Preview", style="white")
    
    # Track successful configurations
    successful_configs = []
    
    # Run all test combinations
    for endpoint in ENDPOINTS:
        for model_name in MODEL_NAMES:
            for auth_method in AUTH_METHODS:
                console.print(f"Testing: {endpoint} with {model_name} using {auth_method['type']} auth...")
                
                result = await test_endpoint(endpoint, model_name, auth_method)
                
                table.add_row(
                    result["endpoint"],
                    result["model"],
                    result["auth"],
                    str(result["status"]),
                    result["result"],
                    result["content_preview"]
                )
                
                if "SUCCESS" in result["result"]:
                    successful_configs.append({
                        "endpoint": result["endpoint"],
                        "model": result["model"],
                        "auth": result["auth"]
                    })
    
    # Display results table
    console.print(table)
    
    # Display successful configurations
    if successful_configs:
        console.print("\n[bold green]Successful Configurations:[/bold green]")
        for i, config in enumerate(successful_configs, 1):
            console.print(f"[green]{i}. Endpoint: {config['endpoint']}")
            console.print(f"   Model: {config['model']}")
            console.print(f"   Auth: {config['auth']}")
            
        # Recommend the best configuration
        console.print("\n[bold green]Recommended Configuration for .env file:[/bold green]")
        best_config = successful_configs[0]  # Take the first successful config as the best
        console.print(f"NEBIUS_API_KEY=your_api_key_here")
        console.print(f"NEBIUS_ENDPOINT={best_config['endpoint']}")
        console.print(f"MODEL_NAME={best_config['model']}")
        console.print(f"\nAuthentication Header: {best_config['auth']} token")
    else:
        console.print("\n[bold red]No successful configurations found.[/bold red]")
        console.print("[red]Please check your API key, network connection, and Nebius account status.[/red]")

if __name__ == "__main__":
    asyncio.run(run_tests())
