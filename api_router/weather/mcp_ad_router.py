from fastapi import APIRouter
from fastapi.responses import JSONResponse
import logging
from config import AGENT_DESCRIPTION_JSON_DOMAIN, DID_DOMAIN, DID_PATH

# Modified route prefix, removed agents/travel/weather
router = APIRouter()


@router.get("/mcp/ad.json")
async def get_weather_agent_description():
    """
    Provide weather agent description information

    Returns:
        Weather agent description in JSON-LD format
    """
    try:
        # Create weather agent description
        weather_agent = {
            "@context": {
                "@vocab": "https://schema.org/",
                "did": "https://w3id.org/did#",
                "ad": "https://agent-network-protocol.com/ad#",
            },
            "@type": "ad:AgentDescription",
            # Modified path in JSON, removed agents/travel/weather
            "@id": f"http://{AGENT_DESCRIPTION_JSON_DOMAIN}/mcp/ad.json",
            "name": "Weather Agent MCP",
            "did": f"did:wba:{DID_DOMAIN}:{DID_PATH}",
            "description": "Weather agent providing weather information lookup services via MCP protocol for cities across the country.",
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
            "ad:interfaces": [
                {
                    "@type": "ad:StructuredInterface",
                    "protocol": "MCP",
                    "url": "https://mcp.amap.com/sse?key=您在高德官网上申请的key",
                    "description": "MCP servers configuration for weather services including AMAP MCP server.",
                }
            ],
        }

        logging.info(f"Returning weather agent description: {weather_agent}")
        return JSONResponse(
            content=weather_agent, media_type="application/json; charset=utf-8"
        )

    except Exception as e:
        logging.error(f"Error getting weather agent description: {str(e)}")
        error_response = {
            "error": "Error getting weather agent description",
            "details": str(e),
        }
        return JSONResponse(
            status_code=500,
            content=error_response,
            media_type="application/json; charset=utf-8",
        )
