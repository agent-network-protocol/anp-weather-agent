#!/usr/bin/env python3
"""
测试按提供商分离的 ad.json 接口
"""

import sys
import os
import asyncio
import json
from fastapi.testclient import TestClient

# 添加项目根目录到 Python 路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from api_router.weather.mcp_agent_ad_router import router
from api_router.weather.mcp_server_manager import mcp_server_manager

# 创建测试客户端
from fastapi import FastAPI
app = FastAPI()
app.include_router(router)
client = TestClient(app)

async def test_provider_ad_endpoints():
    """测试按提供商分离的 ad.json 接口"""
    
    print("=== 测试按提供商分离的 ad.json 接口 ===")
    
    # 首先初始化 MCP 服务器
    print("\n1. 初始化 MCP 服务器...")
    try:
        await mcp_server_manager.initialize_mcp_servers()
        tools_count = len(mcp_server_manager.get_tools_cache())
        print(f"✅ 初始化成功，加载了 {tools_count} 个工具")
    except Exception as e:
        print(f"❌ 初始化失败: {e}")
        return
    
    # 测试获取可用提供商列表
    print("\n2. 测试获取可用提供商列表...")
    try:
        response = client.get("/mcp/agents/providers")
        if response.status_code == 200:
            providers_data = response.json()
            print(f"✅ 获取提供商列表成功")
            print(f"   总提供商数量: {providers_data['total_providers']}")
            for provider in providers_data['providers']:
                print(f"   - {provider['name']}: {provider['tools_count']} 工具, {provider['resources_count']} 资源")
                print(f"     AD URL: {provider['ad_url']}")
        else:
            print(f"❌ 获取提供商列表失败: {response.status_code}")
            print(f"   响应: {response.text}")
    except Exception as e:
        print(f"❌ 获取提供商列表异常: {e}")
    
    # 测试获取特定提供商的 ad.json
    print("\n3. 测试获取 AMAP 提供商的 ad.json...")
    try:
        response = client.get("/mcp/agents/amap/ad.json")
        if response.status_code == 200:
            amap_ad = response.json()
            print(f"✅ 获取 AMAP ad.json 成功")
            print(f"   名称: {amap_ad['name']}")
            print(f"   提供商: {amap_ad.get('provider', 'N/A')}")
            print(f"   接口数量: {len(amap_ad['ad:interfaces'])}")
            print(f"   资源数量: {len(amap_ad['ad:resources'])}")
            
            # 显示前几个工具
            if amap_ad['ad:interfaces']:
                print("   前几个工具:")
                for i, interface in enumerate(amap_ad['ad:interfaces'][:3]):
                    method = interface['schema']['method']
                    description = interface['schema']['description']
                    print(f"     - {method}: {description}")
        else:
            print(f"❌ 获取 AMAP ad.json 失败: {response.status_code}")
            print(f"   响应: {response.text}")
    except Exception as e:
        print(f"❌ 获取 AMAP ad.json 异常: {e}")
    
    # 测试不存在的提供商
    print("\n4. 测试不存在的提供商...")
    try:
        response = client.get("/mcp/agents/nonexistent/ad.json")
        if response.status_code == 404:
            error_data = response.json()
            print(f"✅ 正确返回 404 错误")
            print(f"   错误信息: {error_data['detail']}")
        else:
            print(f"❌ 应该返回 404，但返回了: {response.status_code}")
    except Exception as e:
        print(f"❌ 测试不存在提供商异常: {e}")
    
    # 测试兼容性接口
    print("\n5. 测试兼容性接口（所有提供商汇总）...")
    try:
        response = client.get("/mcp/agents/weather/ad.json")
        if response.status_code == 200:
            all_ad = response.json()
            print(f"✅ 获取汇总 ad.json 成功")
            print(f"   名称: {all_ad['name']}")
            print(f"   接口数量: {len(all_ad['ad:interfaces'])}")
            print(f"   资源数量: {len(all_ad['ad:resources'])}")
        else:
            print(f"❌ 获取汇总 ad.json 失败: {response.status_code}")
            print(f"   响应: {response.text}")
    except Exception as e:
        print(f"❌ 获取汇总 ad.json 异常: {e}")
    
    print("\n=== 测试完成 ===")

if __name__ == "__main__":
    asyncio.run(test_provider_ad_endpoints())
