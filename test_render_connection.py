"""
Test script to verify the API connection on Render deployment.
"""
import os
import sys
import httpx
import argparse
import logging
from dotenv import load_dotenv

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

def test_api_connection(base_url: str, timeout: int = 30):
    """
    Test the connection to the API.
    
    Args:
        base_url: Base URL of the API
        timeout: Timeout in seconds
    """
    logger.info(f"Testing API connection to {base_url}")
    
    # Test endpoints
    endpoints = [
        "/",
        "/api/v1/health/",
        "/docs",
        "/openapi.json"
    ]
    
    success_count = 0
    
    for endpoint in endpoints:
        url = f"{base_url}{endpoint}"
        try:
            logger.info(f"Testing endpoint: {url}")
            response = httpx.get(url, timeout=timeout)
            
            if response.status_code == 200:
                logger.info(f"✅ Success: {url} - Status: {response.status_code}")
                success_count += 1
            else:
                logger.error(f"❌ Failed: {url} - Status: {response.status_code}")
                logger.error(f"Response: {response.text}")
        except Exception as e:
            logger.error(f"❌ Error: {url} - {str(e)}")
    
    # Print summary
    logger.info(f"Summary: {success_count}/{len(endpoints)} endpoints successful")
    
    if success_count == len(endpoints):
        logger.info("✅ All endpoints are working correctly!")
        return True
    else:
        logger.warning("⚠️ Some endpoints failed. Check the logs for details.")
        return False

def test_web_interface(base_url: str, timeout: int = 30):
    """
    Test the web interface.
    
    Args:
        base_url: Base URL of the web interface
        timeout: Timeout in seconds
    """
    logger.info(f"Testing web interface at {base_url}")
    
    try:
        response = httpx.get(base_url, timeout=timeout)
        
        if response.status_code == 200:
            if "Web interface is not available" in response.text:
                logger.warning("⚠️ Web interface is showing the fallback message")
                return False
            else:
                logger.info("✅ Web interface is working correctly!")
                return True
        else:
            logger.error(f"❌ Web interface failed - Status: {response.status_code}")
            logger.error(f"Response: {response.text}")
            return False
    except Exception as e:
        logger.error(f"❌ Error testing web interface: {str(e)}")
        return False

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Test API connection on Render deployment")
    parser.add_argument("--url", type=str, help="Base URL of the API", default=os.getenv("RENDER_URL", "https://appraisalai.onrender.com"))
    parser.add_argument("--timeout", type=int, help="Timeout in seconds", default=30)
    
    args = parser.parse_args()
    
    # Test API connection
    api_success = test_api_connection(args.url, args.timeout)
    
    # Test web interface
    web_success = test_web_interface(args.url, args.timeout)
    
    # Exit with appropriate status code
    if api_success and web_success:
        logger.info("✅ All tests passed!")
        sys.exit(0)
    else:
        logger.warning("⚠️ Some tests failed. Check the logs for details.")
        sys.exit(1)
