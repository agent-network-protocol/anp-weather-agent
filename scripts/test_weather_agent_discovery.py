import json
import logging
import aiohttp
import asyncio
import sys
import os
from pathlib import Path
import argparse
from datetime import datetime, timedelta

# 添加父目录到sys.path以导入根配置
parent_dir = str(Path(__file__).parent.parent)
sys.path.append(parent_dir)

# 从主配置导入
from config import AGENT_DESCRIPTION_JSON_DOMAIN
from scripts.did_auth_client import DIDAuthClient

# 配置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

# 服务器URL
# SERVER_URL = "http://localhost:9870"  # 默认使用本地服务器进行测试
SERVER_URL = "https://agent-weather.xyz"

# DID认证客户端（将在主函数中初始化）
auth_client = None

async def test_weather_agent_root():
    """测试使用agent-weather.xyz域名访问根路径"""
    url = f"{SERVER_URL}/"
    
    logging.info("测试使用agent-weather.xyz域名访问根路径")
    logging.info(f"请求URL: {url}")
    
    try:
        # 根路径不使用认证，只添加Host头
        headers = {"Host": "agent-weather.xyz"}
        
        logging.info(f"使用headers: {headers}")
        
        async with aiohttp.ClientSession() as session:
            async with session.get(url, headers=headers) as response:
                print("\n=== 测试使用agent-weather.xyz域名访问根路径 ===")
                print(f"URL: {url}")
                print(f"状态码: {response.status}")
                
                if response.status == 200:
                    try:
                        data = await response.json()
                        print(f"响应成功，数据长度: {len(str(data))} 字节")
                        print(f"天气智能体名称: {data.get('name', 'N/A')}")
                        print(f"描述开始部分: {data.get('description', 'N/A')[:100]}...")
                        
                        # 检查特殊消息
                        if "special_message" in data:
                            print("找到特殊消息:")
                            print(f"  标题: {data['special_message'].get('title', 'N/A')}")
                        
                        logging.info(f"收到响应，状态码: {response.status}")
                        return data
                    except Exception as e:
                        logging.error(f"解析JSON响应失败: {str(e)}")
                        text = await response.text()
                        print(f"原始响应文本: {text[:200]}...")
                else:
                    logging.error(f"请求失败，状态码: {response.status}")
                    text = await response.text()
                    print(f"错误响应: {text[:200]}...")
                return None
    except Exception as e:
        logging.error(f"请求根路径时发生异常: {str(e)}")
        return None

async def test_well_known_path():
    """测试.well-known/agent-descriptions路径"""
    url = f"{SERVER_URL}/.well-known/agent-descriptions"
    
    logging.info("测试使用agent-weather.xyz域名访问.well-known/agent-descriptions路径")
    logging.info(f"请求URL: {url}")
    
    try:
        # well-known路径不使用认证，只添加Host头
        headers = {"Host": "agent-weather.xyz"}
        
        async with aiohttp.ClientSession() as session:
            async with session.get(url, headers=headers) as response:
                print("\n=== 测试使用agent-weather.xyz域名访问.well-known/agent-descriptions ===")
                print(f"URL: {url}")
                print(f"状态码: {response.status}")
                
                if response.status == 200:
                    try:
                        data = await response.json()
                        print(f"响应成功，数据长度: {len(str(data))} 字节")
                        print(f"类型: {data.get('@type', 'N/A')}")
                        if "items" in data:
                            items_count = len(data["items"])
                            print(f"集合中找到 {items_count} 个项目")
                            for idx, item in enumerate(data["items"]):
                                print(f"  项目 {idx+1}: {item.get('name', 'N/A')} - {item.get('@id', 'N/A')}")
                        logging.info(f"收到响应，状态码: {response.status}")
                        return data
                    except Exception as e:
                        logging.error(f"解析JSON响应失败: {str(e)}")
                        text = await response.text()
                        print(f"原始响应文本: {text[:200]}...")
                else:
                    logging.error(f"请求失败，状态码: {response.status}")
                    text = await response.text()
                    print(f"错误响应: {text[:200]}...")
                return None
    except Exception as e:
        logging.error(f"请求.well-known/agent-descriptions时发生异常: {str(e)}")
        return None

async def test_ad_json_path():
    """测试ad.json路径"""
    url = f"{SERVER_URL}/ad.json"
    
    logging.info("测试使用agent-weather.xyz域名访问ad.json路径")
    logging.info(f"请求URL: {url}")
    
    try:
        # 获取认证头
        auth_headers = auth_client.get_auth_header(SERVER_URL)
        
        # 在请求时添加Host头
        headers = auth_headers.copy()
        # headers["Host"] = "agent-weather.xyz"
        
        async with aiohttp.ClientSession() as session:
            async with session.get(url, headers=headers) as response:
                print("\n=== 测试使用agent-weather.xyz域名访问ad.json ===")
                print(f"URL: {url}")
                print(f"状态码: {response.status}")
                
                # 如果认证成功，更新token
                if response.status == 200:
                    auth_client.update_token(SERVER_URL, dict(response.headers))
                    try:
                        data = await response.json()
                        print(f"响应成功，数据长度: {len(str(data))} 字节")
                        print(f"天气智能体名称: {data.get('name', 'N/A')}")
                        print(f"天气智能体类型: {data.get('@type', 'N/A')}")
                        
                        # 检查安全定义
                        if "ad:securityDefinitions" in data:
                            print("找到安全定义:")
                            for key, value in data["ad:securityDefinitions"].items():
                                print(f"  {key}: {value.get('scheme', 'N/A')}")
                        
                        # 检查接口
                        if "ad:interfaces" in data:
                            interfaces_count = len(data["ad:interfaces"])
                            print(f"找到 {interfaces_count} 个接口:")
                            for idx, interface in enumerate(data["ad:interfaces"]):
                                print(f"  接口 {idx+1}: {interface.get('@type', 'N/A')} - {interface.get('description', 'N/A')}")
                        
                        logging.info(f"收到响应，状态码: {response.status}")
                        return data
                    except Exception as e:
                        logging.error(f"解析JSON响应失败: {str(e)}")
                        text = await response.text()
                        print(f"原始响应文本: {text[:200]}...")
                # 如果认证失败，清除token并重试
                elif response.status == 401:
                    logging.warning("认证以401失败，清除token并重试")
                    auth_client.clear_token(SERVER_URL)
                    
                    # 获取新的认证头并重试
                    auth_headers = auth_client.get_auth_header(SERVER_URL, force_new=True)
                    headers = auth_headers.copy()
                    # headers["Host"] = "agent-weather.xyz"
                    
                    async with session.get(url, headers=headers) as retry_response:
                        if retry_response.status == 200:
                            auth_client.update_token(SERVER_URL, dict(retry_response.headers))
                            data = await retry_response.json()
                            return data
                        else:
                            logging.error(f"重试失败，状态码: {retry_response.status}")
                            text = await retry_response.text()
                            print(f"错误响应: {text[:200]}...")
                else:
                    logging.error(f"请求失败，状态码: {response.status}")
                    text = await response.text()
                    print(f"错误响应: {text[:200]}...")
                return None
    except Exception as e:
        logging.error(f"请求ad.json时发生异常: {str(e)}")
        return None


def get_did_paths(base_path=None):
    """
    获取DID文档和私钥的路径
    
    参数:
        base_path: 基础路径，如果为None则使用当前脚本目录
        
    返回:
        tuple: (did_document_path, private_key_path)
    """
    # 如果没有提供基础路径，使用当前脚本目录
    if base_path is None:
        base_path = Path(__file__).parent
    else:
        base_path = Path(base_path)
    
    # 构建到use_did_test_public目录的路径
    did_dir = base_path / "use_did_test_public"
    
    # 如果目录不存在，尝试父目录
    if not did_dir.exists():
        did_dir = base_path.parent / "use_did_test_public"
    
    # 如果目录仍然不存在，尝试当前工作目录
    if not did_dir.exists():
        did_dir = Path.cwd() / "use_did_test_public"
    
    # 如果目录仍然不存在，使用相对路径
    if not did_dir.exists():
        logging.warning("找不到use_did_test_public目录，使用相对路径")
        did_dir = Path("use_did_test_public")
    
    # 构建DID文档和私钥的路径
    did_document_path = str(did_dir / "did.json")
    private_key_path = str(did_dir / "key-1_private.pem")
    
    logging.info(f"DID文档路径: {did_document_path}")
    logging.info(f"私钥路径: {private_key_path}")
    
    return did_document_path, private_key_path

async def run_tests(did_document_path, private_key_path):
    """使用指定的DID文档和私钥路径运行所有测试"""
    global auth_client
    
    # 初始化DID认证客户端
    auth_client = DIDAuthClient(
        did_document_path=did_document_path,
        private_key_path=private_key_path
    )
    
    logging.info(f"使用文档: {did_document_path} 和密钥: {private_key_path} 初始化DID认证客户端")
    
    # 测试根路径 (/)
    root_data = await test_weather_agent_root()
    
    # 测试.well-known/agent-descriptions路径
    well_known_data = await test_well_known_path()
    
    # 测试ad.json路径
    ad_json_data = await test_ad_json_path()

    
    logging.info("所有测试完成")
    
    # 返回结果
    return {
        "root": root_data is not None,
        "well_known": well_known_data is not None,
        "ad_json": ad_json_data is not None
    }

def parse_arguments():
    """解析命令行参数"""
    parser = argparse.ArgumentParser(description="测试天气智能体发现端点")
    
    parser.add_argument(
        "--did-document", 
        type=str, 
        default=None,
        help="DID文档文件的路径（默认：自动检测）"
    )
    
    parser.add_argument(
        "--private-key", 
        type=str, 
        default=None,
        help="私钥文件的路径（默认：自动检测）"
    )
    
    parser.add_argument(
        "--server-url", 
        type=str, 
        default=SERVER_URL,
        help=f"服务器URL（默认：{SERVER_URL}）"
    )
    
    parser.add_argument(
        "--did-dir", 
        type=str, 
        default=None,
        help="包含DID文件的目录（默认：自动检测）"
    )
    
    return parser.parse_args()

async def main():
    """解析参数并运行测试的主函数"""
    args = parse_arguments()
    
    # 更新全局SERVER_URL
    global SERVER_URL
    SERVER_URL = args.server_url
    
    # 获取DID文档和私钥的路径
    if args.did_document and args.private_key:
        # 如果命令行参数提供了路径，使用它们
        did_document_path = args.did_document
        private_key_path = args.private_key
    else:
        # 否则自动检测路径
        did_document_path, private_key_path = get_did_paths(args.did_dir)
    
    logging.info(f"使用服务器URL: {SERVER_URL}")
    logging.info(f"使用DID文档: {did_document_path}")
    logging.info(f"使用私钥: {private_key_path}")
    
    # 运行测试
    results = await run_tests(did_document_path, private_key_path)
    
    # 打印摘要
    print("\n=== 测试结果摘要 ===")
    print(f"根路径测试: {'✅ 通过' if results['root'] else '❌ 失败'}")
    print(f"well-known路径测试: {'✅ 通过' if results['well_known'] else '❌ 失败'}")
    print(f"AD.json路径测试: {'✅ 通过' if results['ad_json'] else '❌ 失败'}")
    
    # 确定总体结果
    success_count = sum(1 for result in results.values() if result)
    print(f"\n总体: {success_count}/{len(results)} 测试通过")

if __name__ == "__main__":
    asyncio.run(main())