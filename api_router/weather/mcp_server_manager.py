import asyncio
import logging
from typing import Dict, List, Any, Optional, Tuple

# Import MCP SDK
try:
    from mcp import ClientSession
    from mcp.client.sse import sse_client
    MCP_AVAILABLE = True
except ImportError:
    MCP_AVAILABLE = False
    logging.warning("MCP SDK not available, falling back to HTTP-only mode")

from config import AMAP_API_KEY
from config import KuaiDi100_API_KEY

class MCPServerManager:
    """
    管理多个 MCP 服务器配置和初始化的类
    可以轻松扩展以支持更多服务提供商
    """
    
    def __init__(self):
        # 缓存 MCP 服务器数据
        self.mcp_tools_cache: List[Dict[str, Any]] = []
        self.mcp_resources_cache: List[Dict[str, Any]] = []
        self.providers_config = {}
    
    def get_mcp_server_config(self, tool_name: str) -> Optional[Tuple[str, Dict[str, str]]]:
        """
        根据工具名称前缀获取 MCP 服务器配置
        
        Args:
            tool_name: 工具名称（例如，'amap_get_weather'）
            
        Returns:
            (server_url, headers) 元组，如果未找到则返回 None
        """
        # 从工具名称解析提供商前缀
        if '_' not in tool_name:
            return None
        
        provider_prefix = tool_name.split('_')[0].lower()
        
        # 获取提供商配置
        provider_config = self.providers_config.get(provider_prefix)
        if provider_config:
            return provider_config['server_url'], provider_config['headers']
        
        return None
    
    async def initialize_mcp_servers(self):
        """初始化所有支持的 MCP 服务器并缓存它们的工具和资源"""
        # 清除现有缓存
        self.mcp_tools_cache.clear()
        self.mcp_resources_cache.clear()
        
        if not MCP_AVAILABLE:
            logging.warning("MCP SDK not available, skipping MCP server initialization")
            return
        
        try:
            # 尝试连接到每个提供商的 MCP 服务器
            for provider, config in self.providers_config.items():
                server_url = config['server_url']
                
                logging.info(f"Testing connection to {provider} MCP server at {server_url}")
                
                try:
                    # 使用 MCP SDK 连接
                    async with sse_client(server_url) as (read, write):
                        async with ClientSession(read, write) as session:
                            # 初始化 MCP 会话
                            await session.initialize()
                            logging.info(f"Successfully connected and initialized {provider} MCP server")
                            
                            # 从服务器获取工具
                            try:
                                tools_result = await session.list_tools()
                                
                                # 添加服务器工具，并带有提供商属性
                                for tool in tools_result.tools:
                                    tool_info = {
                                        "name": tool.name,  # 保持原始工具名称，不带前缀
                                        "provider": provider,  # 添加提供商作为单独的属性
                                        "description": getattr(tool, "description", "No description available"),
                                        "inputSchema": getattr(tool, "inputSchema", {})
                                    }
                                    self.mcp_tools_cache.append(tool_info)
                                
                                logging.info(f"Loaded {len(tools_result.tools)} tools from {provider} MCP server")
                            except Exception as e:
                                logging.warning(f"Failed to get tools from {provider} MCP server: {str(e)}")
                            
                            # 从服务器获取资源
                            try:
                                resources_result = await session.list_resources()
                                
                                # 添加服务器资源，并带有提供商前缀
                                for resource in resources_result.resources:
                                    resource_info = {
                                        "uri": f"{provider}://{resource.uri}",
                                        "name": f"{provider.upper()} {resource.name}",
                                        "description": getattr(resource, "description", ""),
                                        "mimeType": getattr(resource, "mimeType", "text/plain")
                                    }
                                    self.mcp_resources_cache.append(resource_info)
                                
                                logging.info(f"Loaded {len(resources_result.resources)} resources from {provider} MCP server")
                            except Exception as e:
                                logging.warning(f"Failed to get resources from {provider} MCP server: {str(e)}")
                            
                except Exception as e:
                    # 连接失败，记录错误但不添加回退数据
                    logging.error(f"Failed to connect to {provider} MCP server using MCP SDK: {str(e)}")
            
            logging.info(f"Initialized MCP proxy with {len(self.mcp_tools_cache)} tools and {len(self.mcp_resources_cache)} resources from remote servers")
                    
        except Exception as e:
            logging.error(f"Failed to initialize MCP servers: {str(e)}")
    
    def add_provider(self, provider_name: str, server_url: str, headers: Dict[str, str]):
        """
        添加新的服务提供商配置
        
        Args:
            provider_name: 提供商名称（例如，'kuaidi100'）
            server_url: 服务器 URL
            headers: 请求头
        """
        self.providers_config[provider_name.lower()] = {
            'server_url': server_url,
            'headers': headers
        }
        logging.info(f"Added new provider: {provider_name}")
    
    def get_tools_cache(self) -> List[Dict[str, Any]]:
        """获取工具缓存"""
        return self.mcp_tools_cache
    
    def get_resources_cache(self) -> List[Dict[str, Any]]:
        """获取资源缓存"""
        return self.mcp_resources_cache

# 创建全局单例实例
mcp_server_manager = MCPServerManager()


# # # # # # # # 添加服务商 # # # # # # # #

def add_providers():
    """添加 MCP 服务提供商"""
    
    # 添加快递100提供商配置
    mcp_server_manager.add_provider(
        provider_name="kuaidi",
        server_url=f"http://api.kuaidi100.com/mcp/sse?key={KuaiDi100_API_KEY}",
        headers={}
    )

    mcp_server_manager.add_provider(
        provider_name="amap",
        server_url=f"https://mcp.amap.com/sse?key={AMAP_API_KEY}",
        headers={'X-API-Key': AMAP_API_KEY}
    )
    
    print("MCP 服务提供商已添加")

add_providers()


