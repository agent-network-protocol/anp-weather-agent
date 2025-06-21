import asyncio
import logging
from typing import Dict, List, Any, Optional, Tuple
from fastapi import APIRouter, HTTPException
from fastapi.responses import JSONResponse
import json

# Import MCP SDK - correct way based on reference code
try:
    from mcp import ClientSession
    from mcp.client.sse import sse_client
    MCP_AVAILABLE = True
except ImportError:
    MCP_AVAILABLE = False
    logging.warning("MCP SDK not available, falling back to HTTP-only mode")

from config import AGENT_DESCRIPTION_JSON_DOMAIN, DID_DOMAIN, DID_PATH
from api_router.weather.mcp_server_manager import mcp_server_manager

# Create router with modified route prefix
router = APIRouter()


async def call_mcp_tool_with_sdk(provider: str, tool_name: str, tool_args: Dict[str, Any]) -> Dict[str, Any]:
    """
    Call MCP tool using proper MCP SDK
    
    Args:
        provider: Provider name (e.g., 'amap')
        tool_name: Actual tool name without prefix  
        tool_args: Tool arguments
        
    Returns:
        Tool call result
    """
    if not MCP_AVAILABLE:
        logging.error("MCP SDK not available")
        raise Exception("MCP SDK not available")
    
    # Get server configuration
    server_config = mcp_server_manager.get_mcp_server_config(f"{provider}_dummy")
    if not server_config:
        logging.error(f"No MCP server configured for provider '{provider}'")
        raise Exception(f"No MCP server configured for provider '{provider}'")
    
    server_url, headers = server_config
    
    try:
        # Use proper MCP SDK connection as shown in reference code
        async with sse_client(server_url) as (read, write):
            async with ClientSession(read, write) as session:
                # Initialize the MCP session
                await session.initialize()
                
                # Call the tool using session.call_tool
                result = await session.call_tool(tool_name, tool_args)
                
                # Process result content as shown in reference code
                if hasattr(result, "content") and result.content:
                    content_list = []
                    for content_item in result.content:
                        if hasattr(content_item, "text"):
                            try:
                                # Try to parse as JSON
                                parsed_content = json.loads(content_item.text)
                                content_list.append(parsed_content)
                            except json.JSONDecodeError:
                                # If not JSON, keep as text
                                content_list.append(content_item.text)
                        else:
                            content_list.append(str(content_item))
                    
                    return {
                        "status": "success",
                        "result": content_list[0] if len(content_list) == 1 else content_list,
                        "isError": getattr(result, "isError", False)
                    }
                else:
                    return {
                        "status": "success",
                        "result": "No content returned",
                        "isError": False
                    }
                    
    except Exception as e:
        logging.error(f"MCP tool call failed for {provider}:{tool_name}: {str(e)}")
        raise Exception(f"MCP tool call failed: {str(e)}")

async def read_mcp_resource_with_sdk(provider: str, resource_path: str) -> Dict[str, Any]:
    """
    Read MCP resource using proper MCP SDK
    
    Args:
        provider: Provider name (e.g., 'amap')
        resource_path: Resource path without provider prefix
        
    Returns:
        Resource content
    """
    if not MCP_AVAILABLE:
        raise Exception("MCP SDK not available")
    
    # Get server configuration
    server_config = mcp_server_manager.get_mcp_server_config(f"{provider}_dummy")
    if not server_config:
        raise Exception(f"No MCP server configured for provider '{provider}'")
    
    server_url, headers = server_config
    
    try:
        # Use proper MCP SDK connection as shown in reference code
        async with sse_client(server_url) as (read, write):
            async with ClientSession(read, write) as session:
                # Initialize the MCP session
                await session.initialize()
                
                # Read the resource using session.read_resource
                result = await session.read_resource(resource_path)
                
                # Process result content
                if hasattr(result, "contents") and result.contents:
                    content_list = []
                    for content_item in result.contents:
                        if hasattr(content_item, "text"):
                            try:
                                # Try to parse as JSON
                                parsed_content = json.loads(content_item.text)
                                content_list.append(parsed_content)
                            except json.JSONDecodeError:
                                # If not JSON, keep as text
                                content_list.append(content_item.text)
                        else:
                            content_list.append(str(content_item))
                    
                    return {
                        "status": "success",
                        "content": content_list,
                        "mimeType": getattr(result, "mimeType", "text/plain")
                    }
                else:
                    return {
                        "status": "success", 
                        "content": [],
                        "mimeType": "text/plain"
                    }
                    
    except Exception as e:
        logging.error(f"MCP resource read failed: {str(e)}")
        raise Exception(f"MCP resource read failed: {str(e)}")

@router.get("/mcp/agents/total/ad.json")
async def get_total_agent_description():
    """
    提供所有服务提供商的天气代理描述信息汇总（兼容性接口）

    Returns:
        所有提供商的天气代理描述信息汇总（JSON-LD 格式）
    """
    try:
        # Initialize MCP servers if not already done
        if not mcp_server_manager.get_tools_cache() and not mcp_server_manager.get_resources_cache():
            await mcp_server_manager.initialize_mcp_servers()
        
        # Create weather agent description with MCP tools and resources
        service_agent = {
            "@context": {
                "@vocab": "https://schema.org/",
                "did": "https://w3id.org/did#",
                "ad": "https://agent-network-protocol.com/ad#",
            },
            "@type": "ad:AgentDescription",
            "@id": f"http://{AGENT_DESCRIPTION_JSON_DOMAIN}/mcp/agents/total/ad.json",
            "name": "Anp Service Agent With MCP - Total Providers",
            "did": f"did:wba:{DID_DOMAIN}:{DID_PATH}",
            "description": "The Anp agent provides various services through the MCP protocol.",
            "version": "1.0.0",
            "owner": {
                "@type": "Organization",
                "name": f"{AGENT_DESCRIPTION_JSON_DOMAIN}",
                "@id": f"https://{AGENT_DESCRIPTION_JSON_DOMAIN}",
            },
            "ad:securityDefinitions": {
                "didwba_sc": {
                    "scheme": "didwba",
                    "in": "header",
                    "name": "Authorization",
                }
            },
            "ad:security": "didwba_sc",
            "ad:interfaces": [],
            "ad:resources": []
        }
        
        # Add MCP tools as structured interfaces
        for tool in mcp_server_manager.get_tools_cache():
            interface = {
                "@type": "ad:StructuredInterface",
                "protocol": {
                    "name": "JSON-RPC",
                    "version": "2.0",
                    "transport": "HTTP",
                    "HTTP Method": "POST"
                },
                "schema": {
                    "method": tool["name"],
                    "description": tool["description"],
                    "params": tool["inputSchema"],
                    "annotations": tool.get("annotations", {}),
                },
                "url": f"http://{AGENT_DESCRIPTION_JSON_DOMAIN}/mcp/tools/{tool['provider']}"
            }
            service_agent["ad:interfaces"].append(interface)
        
        # Add MCP resources
        for resource in mcp_server_manager.get_resources_cache():
            resource_item = {
                "@type": "ad:Resource",
                "uri": resource["uri"],
                "name": resource["name"],
                "description": resource["description"],
                "mimeType": resource["mimeType"],
                "url": f"http://{AGENT_DESCRIPTION_JSON_DOMAIN}/mcp/resources?uri={resource['uri']}"
            }
            service_agent["ad:resources"].append(resource_item)

        logging.info(f"Returning weather agent description with {len(mcp_server_manager.get_tools_cache())} tools and {len(mcp_server_manager.get_resources_cache())} resources")
        return JSONResponse(
            content=service_agent, media_type="application/json; charset=utf-8"
        )
    except Exception as e:
        logging.error(f"Failed to get weather agent description: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


@router.get("/mcp/agents/providers")
async def get_available_providers():
    """
    获取所有可用的服务提供商列表

    Returns:
        可用服务提供商的列表
    """
    try:
        # Initialize MCP servers if not already done
        if not mcp_server_manager.get_tools_cache() and not mcp_server_manager.get_resources_cache():
            await mcp_server_manager.initialize_mcp_servers()
        
        # 收集所有可用的提供商
        providers_info = {}
        
        # 从工具中收集提供商信息
        for tool in mcp_server_manager.get_tools_cache():
            provider = tool.get("provider")
            if provider:
                if provider not in providers_info:
                    providers_info[provider] = {
                        "name": provider,
                        "tools_count": 0,
                        "resources_count": 0,
                        "tools": [],
                        "ad_url": f"http://{AGENT_DESCRIPTION_JSON_DOMAIN}/mcp/agents/{provider}/ad.json"
                    }
                providers_info[provider]["tools_count"] += 1
                providers_info[provider]["tools"].append({
                    "name": tool["name"],
                    "description": tool["description"]
                })
        
        # 从资源中收集提供商信息
        for resource in mcp_server_manager.get_resources_cache():
            uri = resource.get("uri", "")
            if "://" in uri:
                provider = uri.split("://")[0]
                if provider in providers_info:
                    providers_info[provider]["resources_count"] += 1
        
        result = {
            "total_providers": len(providers_info),
            "providers": list(providers_info.values())
        }
        
        logging.info(f"Returning {len(providers_info)} available providers")
        return JSONResponse(content=result, media_type="application/json; charset=utf-8")
        
    except Exception as e:
        logging.error(f"Failed to get available providers: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


@router.get("/mcp/agents/{provider}/ad.json")
async def get_service_agent_description_by_provider(provider: str):
    """
    根据指定的提供商返回天气代理描述信息
    
    Args:
        provider: 服务提供商名称（如 'amap', 'kuaidi' 等）

    Returns:
        指定提供商的天气代理描述信息（JSON-LD 格式）
    """
    try:
        # Initialize MCP servers if not already done
        if not mcp_server_manager.get_tools_cache() and not mcp_server_manager.get_resources_cache():
            await mcp_server_manager.initialize_mcp_servers()
        
        # 检查提供商是否存在
        available_providers = set()
        for tool in mcp_server_manager.get_tools_cache():
            available_providers.add(tool.get("provider"))
        for resource in mcp_server_manager.get_resources_cache():
            # 从 URI 中提取提供商名称（格式：provider://...）
            uri = resource.get("uri", "")
            if "://" in uri:
                resource_provider = uri.split("://")[0]
                available_providers.add(resource_provider)
        
        if provider not in available_providers:
            raise HTTPException(
                status_code=404, 
                detail=f"Provider '{provider}' not found. Available providers: {list(available_providers)}"
            )
        
        # 获取指定提供商的工具和资源
        provider_tools = [tool for tool in mcp_server_manager.get_tools_cache() if tool.get("provider") == provider]
        provider_resources = []
        for resource in mcp_server_manager.get_resources_cache():
            uri = resource.get("uri", "")
            if uri.startswith(f"{provider}://"):
                provider_resources.append(resource)
        
        # Create weather agent description for specific provider
        service_agent = {
            "@context": {
                "@vocab": "https://schema.org/",
                "did": "https://w3id.org/did#",
                "ad": "https://agent-network-protocol.com/ad#",
            },
            "@type": "ad:AgentDescription",
            "@id": f"http://{AGENT_DESCRIPTION_JSON_DOMAIN}/mcp/agents/{provider}/ad.json",
            "name": f"Anp Service Agent MCP - {provider.upper()}",
            "did": f"did:wba:{DID_DOMAIN}:{DID_PATH}:{provider}",
            "description": f"The Anp service agent provides various services via {provider.upper()} MCP protocol.",
            "version": "1.0.0",
            "provider": provider,
            "owner": {
                "@type": "Organization",
                "name": f"{AGENT_DESCRIPTION_JSON_DOMAIN}",
                "@id": f"https://{AGENT_DESCRIPTION_JSON_DOMAIN}",
            },
            "ad:securityDefinitions": {
                "didwba_sc": {
                    "scheme": "didwba",
                    "in": "header",
                    "name": "Authorization",
                }
            },
            "ad:security": "didwba_sc",
            "ad:interfaces": [],
            "ad:resources": []
        }
        
        # Add MCP tools for this provider
        for tool in provider_tools:
            interface = {
                "@type": "ad:StructuredInterface",
                "protocol": {
                    "name": "JSON-RPC",
                    "version": "2.0",
                    "transport": "HTTP",
                    "HTTP Method": "POST"
                },
                "schema": {
                    "method": tool["name"],
                    "description": tool["description"],
                    "params": tool["inputSchema"],
                    "annotations": tool.get("annotations", {}),
                },
                "url": f"http://{AGENT_DESCRIPTION_JSON_DOMAIN}/mcp/tools/{provider}"
            }
            service_agent["ad:interfaces"].append(interface)
        
        # Add MCP resources for this provider
        for resource in provider_resources:
            resource_item = {
                "@type": "ad:Resource",
                "uri": resource["uri"],
                "name": resource["name"],
                "description": resource["description"],
                "mimeType": resource["mimeType"],
                "url": f"http://{AGENT_DESCRIPTION_JSON_DOMAIN}/mcp/resources?uri={resource['uri']}"
            }
            service_agent["ad:resources"].append(resource_item)

        logging.info(f"Returning {provider} agent description with {len(provider_tools)} tools and {len(provider_resources)} resources")
        return JSONResponse(
            content=service_agent, media_type="application/json; charset=utf-8"
        )

    except HTTPException:
        raise
    except Exception as e:
        logging.error(f"Failed to get agent description for provider {provider}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

@router.post("/mcp/tools/{provider}")
async def call_mcp_tool(provider: str, request_data: Dict[str, Any]):
    """
    Handle tool calls by forwarding them to the appropriate MCP server based on provider
    Support for JSON-RPC 2.0 format: {"jsonrpc": "2.0", "method": "function_name", "params": {"param1": "value1"}, "id": 1}
    
    Args:
        provider: Provider name (e.g., 'amap')
        request_data: Request data with tool parameters (JSON-RPC 2.0 format or legacy format)
        
    Returns:
        Result from the MCP server in JSON-RPC 2.0 format or legacy format
    """
    try:
        # Handle JSON-RPC 2.0 format or legacy format
        is_jsonrpc = request_data.get("jsonrpc") == "2.0"
        request_id = request_data.get("id") if is_jsonrpc else None
        
        if is_jsonrpc:
            # JSON-RPC 2.0 format: {"jsonrpc": "2.0", "method": "function_name", "params": {"param1": "value1"}, "id": 1}
            tool_name = request_data.get("method")
            arguments = request_data.get("params", {})
            
            if not tool_name:
                raise HTTPException(status_code=400, detail="Missing 'method' field in JSON-RPC request")
                
        else:
            # Legacy format: {"tool_name": "maps_weather", "arguments": {"param1": "value1"}}
            tool_name = request_data.get("tool_name")
            arguments = request_data.get("params", request_data.get("arguments", {}))
            
            if not tool_name:
                raise HTTPException(status_code=400, detail="Missing 'tool_name' field in legacy request")
        
        # Validate that the tool exists for the specified provider
        tool_exists = any(
            tool["name"] == tool_name and tool["provider"] == provider 
            for tool in mcp_server_manager.get_tools_cache()
        )
        
        if not tool_exists:
            logging.error(f"Tool not found: {provider}:{tool_name}")
            raise HTTPException(status_code=404, detail=f"Tool '{tool_name}' not found for provider '{provider}'")
        
        if not arguments:
            logging.warning(f"No arguments found in request for {provider}:{tool_name}")
            
        logging.info(f"Calling MCP tool: {provider}:{tool_name}")
        
        # Call the tool using MCP SDK
        try:
            result = await call_mcp_tool_with_sdk(provider, tool_name, arguments)
            
            # Return response in appropriate format
            if is_jsonrpc:
                # JSON-RPC 2.0 response format
                if result.get("isError", False):
                    response_data = {
                        "jsonrpc": "2.0",
                        "error": {
                            "code": -32000,  # Server error
                            "message": "Tool execution error",
                            "data": result.get("result")
                        },
                        "id": request_id
                    }
                else:
                    response_data = {
                        "jsonrpc": "2.0",
                        "result": result.get("result"),
                        "id": request_id
                    }
            else:
                # Legacy response format
                response_data = {
                    "success": True,
                    "tool": tool_name,
                    "provider": provider,
                    "result": result.get("result"),
                    "isError": result.get("isError", False)
                }

            logging.info(f"MCP tool call response: {response_data}")
            
            return JSONResponse(content=response_data)
            
        except Exception as e:
            logging.error(f"MCP tool call failed for {provider}:{tool_name}: {str(e)}")
            raise Exception(f"MCP tool call error: {str(e)}")
                
    except HTTPException:
        raise
    except Exception as e:
        logging.error(f"Error calling MCP tool '{provider}': {str(e)}")
        
        # Return error response in appropriate format
        is_jsonrpc = request_data.get("jsonrpc") == "2.0"
        request_id = request_data.get("id") if is_jsonrpc else None
        tool_name = request_data.get("method") if is_jsonrpc else request_data.get("tool_name", "unknown")
        
        if is_jsonrpc:
            # JSON-RPC 2.0 error response
            error_response = {
                "jsonrpc": "2.0",
                "error": {
                    "code": -32603,  # Internal error
                    "message": f"Internal error calling tool '{tool_name}' from provider '{provider}'",
                    "data": str(e)
                },
                "id": request_id
            }
        else:
            # Legacy error response
            error_response = {
                "success": False,
                "tool": tool_name,
                "provider": provider,
                "error": f"Internal error calling tool '{tool_name}' from provider '{provider}'",
                "details": str(e)
            }
        
        return JSONResponse(
            status_code=500,
            content=error_response
        )


@router.get("/mcp/resources")
async def get_mcp_resource(uri: str):
    """
    Handle resource requests by forwarding them to the appropriate MCP server based on URI
    
    Args:
        uri: Resource URI to fetch (e.g., 'amap://cities')
        
    Returns:
        Resource content from the MCP server
    """
    try:
        # Validate that the resource exists
        resource_exists = any(resource["uri"] == uri for resource in mcp_server_manager.get_resources_cache())
        if not resource_exists:
            raise HTTPException(status_code=404, detail=f"Resource '{uri}' not found")
        
        # Parse provider from URI
        if '://' not in uri:
            raise HTTPException(status_code=400, detail=f"Invalid resource URI format: '{uri}'")
        
        provider = uri.split('://')[0].lower()
        resource_path = uri.split('://')[1]
        
        logging.info(f"Reading MCP resource: {uri} -> {provider}:{resource_path}")
        
        # Read the resource using MCP SDK
        try:
            result = await read_mcp_resource_with_sdk(provider, resource_path)
            
            return JSONResponse(
                content={
                    "success": True,
                    "uri": uri,
                    "provider": provider,
                    "content": result.get("content", []),
                    "mimeType": result.get("mimeType", "text/plain")
                },
                media_type="application/json; charset=utf-8"
            )
            
        except Exception as e:
            raise Exception(f"MCP resource read error: {str(e)}")
                
    except HTTPException:
        raise
    except Exception as e:
        logging.error(f"Error getting MCP resource '{uri}': {str(e)}")
        
        error_response = {
            "success": False,
            "uri": uri,
            "provider": uri.split('://')[0] if '://' in uri else "unknown",
            "error": f"Error getting resource '{uri}'",
            "details": str(e),
        }
        
        return JSONResponse(
            status_code=500,
            content=error_response,
            media_type="application/json; charset=utf-8"
        )
