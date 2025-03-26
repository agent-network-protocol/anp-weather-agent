from fastapi import APIRouter
from fastapi.responses import JSONResponse
import logging
from config import AGENT_DESCRIPTION_JSON_DOMAIN, DID_DOMAIN, DID_PATH

# Modified route prefix, removed agents/travel/weather
router = APIRouter()


@router.get("/ad.json")
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
            "@id": f"http://{AGENT_DESCRIPTION_JSON_DOMAIN}/ad.json",
            "name": "Weather Agent",
            "did": f"did:wba:{DID_DOMAIN}:{DID_PATH}",
            "description": "Weather agent providing weather information lookup services for cities across the country.",
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
                    "protocol": "YAML",
                    # Modified API file path, removed agents/travel/weather
                    "url": f"http://{AGENT_DESCRIPTION_JSON_DOMAIN}/api_files/weather-info.yaml",
                    "description": "OpenAPI YAML file providing weather query services.",
                },
                {
                    "@type": "ad:StructuredInterface",
                    "protocol": "YAML",
                    # Modified API file path, removed agents/travel/weather
                    "url": f"http://{AGENT_DESCRIPTION_JSON_DOMAIN}/api_files/booking-interface.yaml",
                    "description": "OpenAPI YAML file providing weather information booking services.",
                },
                {
                    "@type": "ad:StructuredInterface",
                    "protocol": "YAML",
                    # Modified API file path, removed agents/travel/weather
                    "url": f"http://{AGENT_DESCRIPTION_JSON_DOMAIN}/api_files/subscription-status-interface.yaml",
                    "description": "OpenAPI YAML file providing weather subscription status query services.",
                },
                {
                    "@type": "ad:NaturalLanguageInterface",
                    "protocol": "YAML",
                    # Modified API file path, removed agents/travel/weather
                    "url": f"http://{AGENT_DESCRIPTION_JSON_DOMAIN}/api_files/nl-interface.yaml",
                    "description": "Interface for interacting with the agent through natural language.",
                },
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
