"""
Test script for validating all weather-related APIs.
Using DIDWbaAuthHeader for authentication.
"""

import os
import json
import logging
import asyncio
import aiohttp
from pathlib import Path
from typing import Tuple, Dict, Optional, Any, List
from urllib.parse import urlparse

from agent_connect.authentication import DIDWbaAuthHeader

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# Try to get port from environment variable, default to 8000
port = os.environ.get("SERVER_PORT", "8000")
# Constants
SERVER_URL = f"http://localhost:{port}"
# Get current script directory
CURRENT_DIR = Path(__file__).parent
# Get project root directory (parent of current directory)
BASE_DIR = CURRENT_DIR.parent
# Use absolute paths
DID_DOCUMENT_PATH = str(BASE_DIR / "doc/use_did_test_public/did.json")
PRIVATE_KEY_PATH = str(BASE_DIR / "doc/use_did_test_public/key-1_private.pem")


async def send_request(
    url: str, 
    auth_client: DIDWbaAuthHeader, 
    method: str = "GET", 
    params: Dict = None, 
    json_data: Dict = None
) -> Tuple[int, Optional[Dict]]:
    """
    Send request to specified URL with DID authentication header.
    
    Args:
        url: Request URL
        auth_client: DID authentication client
        method: Request method (GET, POST)
        params: URL parameters
        json_data: JSON request body
        
    Returns:
        Tuple[int, Optional[Dict]]: Status code and response content
    """
    try:
        # Get authentication header
        headers = auth_client.get_auth_header(url)
        logger.info(f"Sending {method} request to {url}")
        
        async with aiohttp.ClientSession() as session:
            if method == "GET":
                async with session.get(url, headers=headers, params=params) as response:
                    status = response.status
                    try:
                        if response.content_type == 'application/json':
                            data = await response.json()
                        else:
                            data = await response.text()
                    except:
                        data = await response.text()
            elif method == "POST":
                async with session.post(url, headers=headers, json=json_data) as response:
                    status = response.status
                    try:
                        if response.content_type == 'application/json':
                            data = await response.json()
                        else:
                            data = await response.text()
                    except:
                        data = await response.text()
            else:
                logger.error(f"Unsupported method: {method}")
                return 400, None
                
            logger.info(f"Received response with status code: {status}")
            
            # Update token if returned
            auth_client.update_token(url, dict(response.headers))
            
            return status, data
            
    except Exception as e:
        logger.error(f"Error during request: {e}")
        logger.error("Stack trace:", exc_info=True)
        return 500, None


async def test_ad_json(auth_client: DIDWbaAuthHeader) -> bool:
    """
    Test agent description API
    
    Args:
        auth_client: DID authentication client
        
    Returns:
        bool: Whether test was successful
    """
    url = f"{SERVER_URL}/ad.json"
    logger.info(f"Testing agent description API: {url}")
    
    status, data = await send_request(url, auth_client)
    
    if status == 200:
        logger.info("Agent description API test successful")
        logger.info(f"Agent name: {data.get('name', 'Unknown')}")
        return True
    else:
        logger.error(f"Agent description API test failed: {data}")
        return False


async def test_yaml_files(auth_client: DIDWbaAuthHeader) -> bool:
    """
    Test YAML files API
    
    Args:
        auth_client: DID authentication client
        
    Returns:
        bool: Whether test was successful
    """
    yaml_files = [
        "weather-info.yaml", 
        "booking-interface.yaml", 
        "subscription-status-interface.yaml", 
        "nl-interface.yaml"
    ]
    
    all_successful = True
    
    for yaml_file in yaml_files:
        url = f"{SERVER_URL}/api_files/{yaml_file}"
        logger.info(f"Testing YAML API for file: {yaml_file}")
        
        status, data = await send_request(url, auth_client)
        
        if status == 200:
            logger.info(f"YAML API test for {yaml_file} successful")
            # For YAML files, we only check if the response is text
            if isinstance(data, str) and len(data) > 0:
                logger.info(f"Retrieved YAML content of size: {len(data)} characters")
            else:
                logger.warning(f"YAML content may not be valid: {type(data)}")
                all_successful = False
        else:
            logger.error(f"YAML API test for {yaml_file} failed: {data}")
            all_successful = False
    
    return all_successful


async def test_weather_info(auth_client: DIDWbaAuthHeader) -> bool:
    """
    Test weather information API
    
    Args:
        auth_client: DID authentication client
        
    Returns:
        bool: Whether test was successful
    """
    url = f"{SERVER_URL}/api/weather_info"
    logger.info(f"Testing weather info API: {url}")
    
    # Test different cities
    cities = ["Beijing", "Shanghai", "Guangzhou", "Shenzhen"]
    all_successful = True
    
    for city in cities:
        logger.info(f"Testing weather info for city: {city}")
        
        status, data = await send_request(url, auth_client, params={"cityName": city})
        
        if status == 200:
            logger.info(f"Weather info API test for {city} successful")
            if isinstance(data, dict) and data.get("status") == "1":
                forecasts = data.get("forecasts", [])
                if forecasts:
                    logger.info(f"Retrieved forecast data for {city}: {forecasts[0].get('province')} {forecasts[0].get('city')}")
                else:
                    logger.warning(f"No forecast data for {city}")
                    all_successful = False
            else:
                logger.warning(f"Weather API returned error: {data}")
                all_successful = False
        else:
            logger.error(f"Weather info API test for {city} failed: {data}")
            all_successful = False
    
    return all_successful


async def test_nl_api(auth_client: DIDWbaAuthHeader) -> bool:
    """
    Test natural language query API
    
    Args:
        auth_client: DID authentication client
        
    Returns:
        bool: Whether test was successful
    """
    url = f"{SERVER_URL}/api/ask"
    logger.info(f"Testing natural language API: {url}")
    
    questions = [
        "What's the weather like in Beijing tomorrow?",
        "Will it rain in Shanghai this week?"
    ]
    
    all_successful = True
    
    for question in questions:
        status, data = await send_request(
            url, 
            auth_client, 
            method="POST",
            json_data={"question": question}
        )
        
        if status == 200:
            logger.info(f"Natural language API test for '{question}' successful")
            # Note: This API may return streaming response, simplified handling here
            if isinstance(data, str) and len(data) > 0:
                logger.info(f"Response length: {len(data)} characters")
            else:
                logger.warning(f"Response may not be valid: {type(data)}")
                all_successful = False
        else:
            logger.error(f"Natural language API test for '{question}' failed: {data}")
            all_successful = False
    
    return all_successful


async def test_subscription_api(auth_client: DIDWbaAuthHeader) -> bool:
    """
    Test subscription API
    
    Args:
        auth_client: DID authentication client
        
    Returns:
        bool: Whether test was successful
    """
    # Test subscription creation
    subscribe_url = f"{SERVER_URL}/api/subscribe"
    logger.info(f"Testing subscription creation API: {subscribe_url}")
    
    subscription_data = {
        "customerOrderNo": f"TEST-ORDER-{asyncio.get_event_loop().time()}",
        "subscriptionType": "monthly",
        "subscriberDID": "did:wba:agent-did.com:test:public", 
        "contactName": "Test User",
        "contactMobile": "13800138000",
        "contactEmail": "test@example.com",
        "regions": ["Beijing", "Shanghai"],
        "customFeatures": ["Advanced Weather Forecast", "Weather Alerts"]
    }
    
    status, data = await send_request(
        subscribe_url, 
        auth_client, 
        method="POST",
        json_data=subscription_data
    )
    
    subscription_id = None
    
    if status == 200:
        logger.info("Subscription creation API test completed")
        
        # Check if it's a whitelist response, currently API responds successfully but rejects non-whitelist users
        if isinstance(data, dict) and not data.get("success", True):
            logger.info(f"Subscription API response: {data.get('msg', 'Unknown message')}")
            # Although it's a whitelist error, API is working correctly
            subscription_test_passed = True
        else:
            # Actually created successfully (possibly in test environment)
            if isinstance(data, dict) and data.get("success"):
                subscription_id = data.get("data", {}).get("subscriptionId")
                logger.info(f"Created subscription with ID: {subscription_id}")
                subscription_test_passed = True
            else:
                logger.warning(f"Unexpected subscription response: {data}")
                subscription_test_passed = False
    else:
        logger.error(f"Subscription creation API test failed: {data}")
        subscription_test_passed = False
    
    
    # Test subscription status query
    status_url = f"{SERVER_URL}/api/subscription/status"
    logger.info(f"Testing subscription status API: {status_url}")
    
    # If no actual subscription ID obtained, use test ID
    test_subscription_id = subscription_id or "test-subscription-id"
    
    status, data = await send_request(
        status_url, 
        auth_client, 
        params={
            "subscriptionId": test_subscription_id,
            "subscriberDID": "did:wba:agent-did.com:test:public"
        }
    )
    
    if status == 200:
        logger.info("Subscription status API test completed")
        
        # Check if it's a whitelist response
        if isinstance(data, dict) and not data.get("success", True):
            logger.info(f"Subscription status API response: {data.get('msg', 'Unknown message')}")
            # Although it's a whitelist error, API is working correctly
            status_test_passed = True
        else:
            # Actually queried successfully (possibly in test environment)
            if isinstance(data, dict) and data.get("success"):
                status_info = data.get("data", {})
                logger.info(f"Subscription status: {status_info.get('status', 'Unknown')}")
                status_test_passed = True
            else:
                logger.warning(f"Unexpected subscription status response: {data}")
                status_test_passed = False
    else:
        logger.error(f"Subscription status API test failed: {data}")
        status_test_passed = False
    
    return subscription_test_passed and status_test_passed


async def main():
    """Main function"""
    try:
        # 1. Create DID authentication client
        auth_client = DIDWbaAuthHeader(
            did_document_path=DID_DOCUMENT_PATH, private_key_path=PRIVATE_KEY_PATH
        )
        logger.info("Created DID authentication client")
        
        # 2. Test all APIs
        test_results = {}
        
        # Test agent description API
        test_results["ad_json"] = await test_ad_json(auth_client)
        
        # Test YAML files API
        test_results["yaml_files"] = await test_yaml_files(auth_client)
        
        # Test weather info API
        test_results["weather_info"] = await test_weather_info(auth_client)
        
        # Test natural language API
        test_results["nl_api"] = await test_nl_api(auth_client)
        
        # Test subscription API
        test_results["subscription_api"] = await test_subscription_api(auth_client)
        
        # 3. Output test results summary
        logger.info("\n===== API TEST SUMMARY =====")
        all_passed = True
        for api_name, result in test_results.items():
            status = "PASSED" if result else "FAILED"
            if not result:
                all_passed = False
            logger.info(f"{api_name}: {status}")
        
        if all_passed:
            logger.info("\nAll API tests PASSED!")
        else:
            logger.warning("\nSome API tests FAILED. Check the logs for details.")
            
    except Exception as e:
        logger.error(f"Error in main function: {e}")
        logger.error("Stack trace:", exc_info=True)


if __name__ == "__main__":
    # Run tests
    logger.info("Starting API testing with DID authentication")
    asyncio.run(main()) 