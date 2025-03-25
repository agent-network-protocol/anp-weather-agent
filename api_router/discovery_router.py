from fastapi import APIRouter, Request
from fastapi.responses import JSONResponse
import logging
import os


router = APIRouter()

# 获取当前文件所在目录
current_directory = os.path.dirname(os.path.abspath(__file__))

@router.get("/.well-known/agent-descriptions")
async def get_agent_descriptions(request: Request):
    """
    Process requests for agent descriptions following the Agent Discovery Service Protocol (ADSP).
    Returns a collection of agent descriptions for the requested domain.
    """
    # 获取主机名
    host = request.headers.get("host", "")
    logging.info(f"Received agent-descriptions request for host: {host}")
    
    # 提取域名
    domain = host.split(":")[0] if ":" in host else host
    
    # 仅当域名是agent-weather.xyz时返回对应的数据
    if domain == "agent-weather.xyz":
        # 构建符合ANP智能体发现协议的响应
        response_data = {
            "@context": {
                "@vocab": "https://schema.org/",
                "did": "https://w3id.org/did#",
                "ad": "https://agent-network-protocol.com/ad#"
            },
            "@type": "CollectionPage",
            "url": f"https://{domain}/.well-known/agent-descriptions",
            "items": [
                {
                    "@type": "ad:AgentDescription",
                    "name": "Weather Information Agent",
                    "@id": f"https://{domain}/ad.json"
                }
            ]
        }
        return JSONResponse(content=response_data)
    else:
        # 对于其他域名，返回空的集合页面
        response_data = {
            "@context": {
                "@vocab": "https://schema.org/",
                "did": "https://w3id.org/did#",
                "ad": "https://agent-network-protocol.com/ad#"
            },
            "@type": "CollectionPage",
            "url": f"https://{domain}/.well-known/agent-descriptions",
            "items": []
        }
        return JSONResponse(content=response_data)
