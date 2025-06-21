"""
Test script for MCP agent weather APIs.
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
import requests

from agent_connect.authentication import DIDWbaAuthHeader

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# Constants
SERVER_URL = "http://localhost:9870"
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
    json_data: Dict = None,
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
                        if response.content_type == "application/json":
                            data = await response.json()
                        else:
                            data = await response.text()
                    except:
                        data = await response.text()
            elif method == "POST":
                async with session.post(
                    url, headers=headers, json=json_data
                ) as response:
                    status = response.status
                    try:
                        if response.content_type == "application/json":
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


async def test_mcp_ad_json(auth_client: DIDWbaAuthHeader) -> bool:
    """
    Test MCP agent description API

    Args:
        auth_client: DID authentication client

    Returns:
        bool: Whether test was successful
    """
    url = f"{SERVER_URL}/mcp/agents/total/ad.json"
    logger.info(f"Testing MCP agent description API: {url}")

    status, data = await send_request(url, auth_client)

    if status == 200:
        logger.info("MCP agent description API test successful")
        logger.info(f"Agent name: {data.get('name', 'Unknown')}")
        logger.info(f"Found {len(data.get('ad:interfaces', []))} MCP interfaces")
        logger.info(f"Found {len(data.get('ad:resources', []))} MCP resources")
        
        # Print interface details
        for interface in data.get('ad:interfaces', []):
            logger.info(f"  Interface: {interface.get('name')} - {interface.get('description')}")
            logger.info(f"    Protocol: {interface.get('protocol')}")
            logger.info(f"    URL: {interface.get('url')}")
        
        # Print resource details
        for resource in data.get('ad:resources', []):
            logger.info(f"  Resource: {resource.get('name')} - {resource.get('description')}")
            logger.info(f"    URI: {resource.get('uri')}")
            logger.info(f"    URL: {resource.get('url')}")
        
        return True
    else:
        logger.error(f"MCP agent description API test failed: {data}")
        return False


async def test_mcp_tools(auth_client: DIDWbaAuthHeader) -> bool:
    """
    Test MCP tool calls

    Args:
        auth_client: DID authentication client

    Returns:
        bool: Whether test was successful
    """
    # Test different tools with new provider/tool_name format
    tools_tests = [
        {
            "provider": "amap",
            "tool_name": "maps_weather",
            "params": {
                "city": "北京"
            }
        },
        {
            "provider": "amap",
            "tool_name": "maps_text_search",
            "params": {
                "keywords": "咖啡厅",
                "city": "北京"
            }
        }
    ]

    all_successful = True

    for i, test_case in enumerate(tools_tests):
        if i > 0:  # Add delay between tool tests
            await asyncio.sleep(1)
            
        provider = test_case["provider"]
        tool_name = test_case["tool_name"]
        params = test_case["params"]
        
        url = f"{SERVER_URL}/mcp/tools/{provider}"
        logger.info(f"Testing MCP tool call: {provider}:{tool_name}")

        # JSON-RPC 2.0 format request
        request_data = {
            "jsonrpc": "2.0",
            "method": tool_name,
            "params": params,
            "id": i + 1  # Use unique ID for each request
        }

        status, data = await send_request(url, auth_client, method="POST", json_data=request_data)

        if status == 200:
            logger.info(f"MCP tool call for {provider}:{tool_name} successful")
            if isinstance(data, dict):
                # Handle JSON-RPC 2.0 response format
                if "jsonrpc" in data and data.get("jsonrpc") == "2.0":
                    if "result" in data:
                        logger.info(f"JSON-RPC result: {data.get('result', {})}")
                    elif "error" in data:
                        logger.warning(f"JSON-RPC error: {data.get('error')}")
                        all_successful = False
                    else:
                        logger.warning(f"Invalid JSON-RPC response format")
                        all_successful = False
                else:
                    # Handle legacy response format
                    if data.get("success"):
                        logger.info(f"Tool result: {data.get('result', {})}")
                        if data.get("isError"):
                            logger.warning(f"Tool returned error: {data.get('result')}")
                            all_successful = False
                    else:
                        logger.warning(f"Tool call failed: {data.get('error', 'Unknown error')}")
                        all_successful = False
            else:
                logger.warning(f"Unexpected response format: {type(data)}")
                all_successful = False
        else:
            logger.error(f"MCP tool call for {provider}:{tool_name} failed: {data}")
            all_successful = False

    return all_successful


async def test_mcp_resources(auth_client: DIDWbaAuthHeader) -> bool:
    """
    Test MCP resource access

    Args:
        auth_client: DID authentication client

    Returns:
        bool: Whether test was successful
    """
    # Test different resources - skip since AMAP MCP server provides no resources
    resources_tests = []

    all_successful = True

    for i, resource_uri in enumerate(resources_tests):
        if i > 0:  # Add delay between resource tests
            await asyncio.sleep(1)
            
        url = f"{SERVER_URL}/mcp/resources"
        logger.info(f"Testing MCP resource access: {resource_uri}")

        status, data = await send_request(url, auth_client, params={"uri": resource_uri})

        if status == 200:
            logger.info(f"MCP resource access for {resource_uri} successful")
            if isinstance(data, dict):
                if data.get("success"):
                    content = data.get("content", [])
                    mime_type = data.get("mimeType", "text/plain")
                    logger.info(f"Resource content type: {mime_type}")
                    logger.info(f"Resource content size: {len(str(content))} characters")
                else:
                    logger.warning(f"Resource access failed: {data.get('error', 'Unknown error')}")
                    all_successful = False
            else:
                logger.warning(f"Unexpected response format: {type(data)}")
                all_successful = False
        else:
            logger.error(f"MCP resource access for {resource_uri} failed: {data}")
            all_successful = False

    return all_successful


async def main():
    """Main function"""
    try:
        # 1. Create DID authentication client
        auth_client = DIDWbaAuthHeader(
            did_document_path=DID_DOCUMENT_PATH, private_key_path=PRIVATE_KEY_PATH
        )
        logger.info("Created DID authentication client")

        # 2. Test all APIs with delays between requests to avoid nonce conflicts
        test_results = {}

        # Test MCP agent description API  
        test_results["mcp_ad_json"] = await test_mcp_ad_json(auth_client)
        await asyncio.sleep(1)  # Wait 1 second to avoid nonce conflicts

        # Test MCP tool calls
        test_results["mcp_tools"] = await test_mcp_tools(auth_client)
        await asyncio.sleep(1)  # Wait 1 second to avoid nonce conflicts

        # Test MCP resource access
        test_results["mcp_resources"] = await test_mcp_resources(auth_client)

        # 3. Output test result summary
        logger.info("\n===== MCP API TEST SUMMARY =====")
        all_passed = True
        for api_name, result in test_results.items():
            status = "PASSED" if result else "FAILED"
            if not result:
                all_passed = False
            logger.info(f"{api_name}: {status}")

        if all_passed:
            logger.info("\nAll MCP API tests PASSED!")
        else:
            logger.warning("\nSome MCP API tests FAILED. Check the logs for details.")

    except Exception as e:
        logger.error(f"Error in main function: {e}")
        logger.error("Stack trace:", exc_info=True)


if __name__ == "__main__":
    # Run tests
    logger.info("Starting MCP API testing with DID authentication")
    asyncio.run(main()) 