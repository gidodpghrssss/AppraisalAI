"""
Script to fix database schema issues and test API endpoints in the Render deployment.
"""
import os
import sys
import logging
import requests
import time
from fix_database_schema import fix_database_schema

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Get the Render service URL from environment or use a default value
RENDER_URL = os.getenv("RENDER_URL", "https://appraisal-ai.onrender.com")

def test_api_endpoints():
    """Test API endpoints to ensure they are accessible."""
    logger.info(f"Testing API endpoints at {RENDER_URL}")
    
    # List of endpoints to test
    endpoints = [
        "/api/v1/health/",
        "/api/v1/direct/test",
        "/api/v1/clients/",
        "/api/v1/projects/",
        "/api/v1/properties/"
    ]
    
    success_count = 0
    failure_count = 0
    
    for endpoint in endpoints:
        url = f"{RENDER_URL}{endpoint}"
        try:
            logger.info(f"Testing endpoint: {url}")
            response = requests.get(url, timeout=10)
            
            if response.status_code in [200, 201, 202, 204]:
                logger.info(f"✅ Endpoint {endpoint} is accessible (Status: {response.status_code})")
                success_count += 1
            else:
                logger.error(f"❌ Endpoint {endpoint} returned status code {response.status_code}")
                failure_count += 1
        except Exception as e:
            logger.error(f"❌ Error accessing endpoint {endpoint}: {e}")
            failure_count += 1
    
    # Test web interface
    try:
        logger.info(f"Testing web interface: {RENDER_URL}")
        response = requests.get(RENDER_URL, timeout=10)
        
        if response.status_code == 200:
            logger.info(f"✅ Web interface is accessible (Status: {response.status_code})")
            success_count += 1
        else:
            logger.error(f"❌ Web interface returned status code {response.status_code}")
            failure_count += 1
    except Exception as e:
        logger.error(f"❌ Error accessing web interface: {e}")
        failure_count += 1
    
    logger.info(f"API test summary: {success_count} successes, {failure_count} failures")
    return success_count, failure_count

def main():
    """Main function to fix database schema and test API endpoints."""
    logger.info("Starting database schema fix and API endpoint testing")
    
    # Fix database schema
    logger.info("Step 1: Fixing database schema")
    schema_success = fix_database_schema()
    
    if schema_success:
        logger.info("Database schema fix completed successfully")
    else:
        logger.error("Database schema fix failed")
        sys.exit(1)
    
    # Wait for changes to take effect
    logger.info("Waiting for changes to take effect...")
    time.sleep(5)
    
    # Test API endpoints
    logger.info("Step 2: Testing API endpoints")
    success_count, failure_count = test_api_endpoints()
    
    if failure_count == 0:
        logger.info("All API endpoints are accessible")
        return True
    else:
        logger.warning(f"{failure_count} API endpoints are not accessible")
        return False

if __name__ == "__main__":
    success = main()
    if success:
        logger.info("Fix and test completed successfully")
        sys.exit(0)
    else:
        logger.error("Fix and test completed with errors")
        sys.exit(1)
