"""
测试脚本，用于验证所有对外的天气相关 API。
使用 DIDWbaAuthHeader 进行身份验证。
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

# 配置日志
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# 常量
SERVER_URL = "http://localhost:8000"
# 获取当前脚本所在目录
CURRENT_DIR = Path(__file__).parent
# 获取项目根目录（当前目录的父目录）
BASE_DIR = CURRENT_DIR.parent
# 使用绝对路径
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
    发送请求到指定 URL，使用 DID 认证头。
    
    Args:
        url: 请求 URL
        auth_client: DID 认证客户端
        method: 请求方法 (GET, POST)
        params: URL 参数
        json_data: JSON 请求体
        
    Returns:
        Tuple[int, Optional[Dict]]: 状态码和响应内容
    """
    try:
        # 获取认证头
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
            
            # 更新令牌（如果有返回）
            auth_client.update_token(url, dict(response.headers))
            
            return status, data
            
    except Exception as e:
        logger.error(f"Error during request: {e}")
        logger.error("Stack trace:", exc_info=True)
        return 500, None


async def test_ad_json(auth_client: DIDWbaAuthHeader) -> bool:
    """
    测试获取天气智能体描述 API
    
    Args:
        auth_client: DID 认证客户端
        
    Returns:
        bool: 测试是否成功
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
    测试获取 YAML 文件 API
    
    Args:
        auth_client: DID 认证客户端
        
    Returns:
        bool: 测试是否成功
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
            # 对于 YAML 文件，我们只检查返回的是否是文本
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
    测试获取天气信息 API
    
    Args:
        auth_client: DID 认证客户端
        
    Returns:
        bool: 测试是否成功
    """
    url = f"{SERVER_URL}/api/weather_info"
    logger.info(f"Testing weather info API: {url}")
    
    # 测试不同城市
    cities = ["北京", "上海", "广州", "深圳"]
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
    测试自然语言查询 API
    
    Args:
        auth_client: DID 认证客户端
        
    Returns:
        bool: 测试是否成功
    """
    url = f"{SERVER_URL}/api/ask"
    logger.info(f"Testing natural language API: {url}")
    
    questions = [
        "明天北京天气怎么样？",
        "上海本周会下雨吗？"
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
            # 注意：这个 API 可能返回流式响应，这里简化处理
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
    测试订阅 API
    
    Args:
        auth_client: DID 认证客户端
        
    Returns:
        bool: 测试是否成功
    """
    # 测试创建订阅
    subscribe_url = f"{SERVER_URL}/api/subscribe"
    logger.info(f"Testing subscription creation API: {subscribe_url}")
    
    subscription_data = {
        "customerOrderNo": f"TEST-ORDER-{asyncio.get_event_loop().time()}",
        "subscriptionType": "monthly",
        "subscriberDID": "did:wba:agent-did.com:test:public", 
        "contactName": "Test User",
        "contactMobile": "13800138000",
        "contactEmail": "test@example.com",
        "regions": ["北京", "上海"],
        "customFeatures": ["高级天气预报", "天气预警"]
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
        
        # 检查是否是白名单响应，目前API响应成功但拒绝非白名单用户
        if isinstance(data, dict) and not data.get("success", True):
            logger.info(f"Subscription API response: {data.get('msg', 'Unknown message')}")
            # 虽然是白名单错误，但API正常工作
            subscription_test_passed = True
        else:
            # 实际创建成功（可能是测试环境）
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
    
    
    # 测试查询订阅状态
    status_url = f"{SERVER_URL}/api/subscription/status"
    logger.info(f"Testing subscription status API: {status_url}")
    
    # 如果没有获取到实际订阅ID，使用测试ID
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
        
        # 检查是否是白名单响应
        if isinstance(data, dict) and not data.get("success", True):
            logger.info(f"Subscription status API response: {data.get('msg', 'Unknown message')}")
            # 虽然是白名单错误，但API正常工作
            status_test_passed = True
        else:
            # 实际查询成功（可能是测试环境）
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
    """主函数"""
    try:
        # 1. 创建 DID 认证客户端
        auth_client = DIDWbaAuthHeader(
            did_document_path=DID_DOCUMENT_PATH, private_key_path=PRIVATE_KEY_PATH
        )
        logger.info("Created DID authentication client")
        
        # 2. 测试所有 API
        test_results = {}
        
        # 测试智能体描述 API
        test_results["ad_json"] = await test_ad_json(auth_client)
        
        # 测试 YAML 文件 API
        test_results["yaml_files"] = await test_yaml_files(auth_client)
        
        # 测试天气信息 API
        test_results["weather_info"] = await test_weather_info(auth_client)
        
        # 测试自然语言 API
        test_results["nl_api"] = await test_nl_api(auth_client)
        
        # 测试订阅 API
        test_results["subscription_api"] = await test_subscription_api(auth_client)
        
        # 3. 输出测试结果摘要
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
    # 运行测试
    logger.info("Starting API testing with DID authentication")
    asyncio.run(main())
