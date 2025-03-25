from fastapi import APIRouter
from fastapi.responses import JSONResponse
import logging
from config import AGENT_DESCRIPTION_JSON_DOMAIN, DID_DOMAIN, DID_PATH

# 修改路由前缀，去掉 agents/travel/weather
router = APIRouter()

@router.get("/ad.json")
async def get_weather_agent_description():
    """
    提供天气智能体的描述信息
    
    Returns:
        天气智能体描述的JSON-LD格式
    """
    try:
        # 创建天气智能体描述
        weather_agent = {
            "@context": {
                "@vocab": "https://schema.org/",
                "did": "https://w3id.org/did#",
                "ad": "https://agent-network-protocol.com/ad#"
            },
            "@type": "ad:AgentDescription",
            # 修改 JSON 中的路径，去掉 agents/travel/weather
            "@id": f"https://{AGENT_DESCRIPTION_JSON_DOMAIN}/ad.json",
            "name": "天气智能体",
            "did": f"did:wba:{DID_DOMAIN}:{DID_PATH}",
            "description": "天气智能体，提供全国城市天气信息查询服务。",
            "version": "1.0.0",
            "owner": {
                "@type": "Organization",
                "name": f"{AGENT_DESCRIPTION_JSON_DOMAIN}",
                "@id": f"https://{AGENT_DESCRIPTION_JSON_DOMAIN}"
            },
            "ad:securityDefinitions": {
                "didwba_sc": {
                    "scheme": "didwba",
                    "in": "header",
                    "name": "Authorization"
                }
            },
            "ad:security": "didwba_sc",
            "ad:interfaces": [
                {
                    "@type": "ad:StructuredInterface",
                    "protocol": "YAML",
                    # 修改 API 文件路径，去掉 agents/travel/weather
                    "url": f"https://{AGENT_DESCRIPTION_JSON_DOMAIN}/api_files/weather-info.yaml",
                    "description": "提供天气查询服务的OpenAPI的YAML文件。"
                },
                {
                    "@type": "ad:StructuredInterface",
                    "protocol": "YAML",
                    # 修改 API 文件路径，去掉 agents/travel/weather
                    "url": f"https://{AGENT_DESCRIPTION_JSON_DOMAIN}/api_files/booking-interface.yaml",
                    "description": "提供天气信息预订服务的OpenAPI的YAML文件。"
                },
                {
                    "@type": "ad:StructuredInterface",
                    "protocol": "YAML",
                    # 修改 API 文件路径，去掉 agents/travel/weather
                    "url": f"https://{AGENT_DESCRIPTION_JSON_DOMAIN}/api_files/subscription-status-interface.yaml",
                    "description": "提供天气订阅状态查询服务的OpenAPI的YAML文件。"
                },
                {
                    "@type": "ad:NaturalLanguageInterface",
                    "protocol": "YAML",
                    # 修改 API 文件路径，去掉 agents/travel/weather
                    "url": f"https://{AGENT_DESCRIPTION_JSON_DOMAIN}/api_files/nl-interface.yaml",
                    "description": "提供通过自然语言与智能代理交互的接口。"
                }
            ]
        }
        
        logging.info(f"返回天气智能体描述: {weather_agent}")
        return JSONResponse(content=weather_agent, media_type="application/json; charset=utf-8")
        
    except Exception as e:
        logging.error(f"获取天气智能体描述时出错: {str(e)}")
        error_response = {
            "error": "获取天气智能体描述时出错",
            "details": str(e)
        }
        return JSONResponse(
            status_code=500,
            content=error_response,
            media_type="application/json; charset=utf-8"
        )