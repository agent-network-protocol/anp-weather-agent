from typing import  Optional
from fastapi import APIRouter,  Query
from pydantic import BaseModel
import aiohttp
import json
import traceback
import logging
from pathlib import Path
from config import AMAP_WEATHER_API_URL, AMAP_API_KEY

# Modified route prefix, removed agents/travel/weather
router = APIRouter()

# AMAP Weather API parameters
AMAP_EXTENSIONS = "all"

# Data models
class WeatherInfoRequest(BaseModel):
    """Weather query request model"""
    cityName: str

class WeatherInfoResponse(BaseModel):
    """Weather query response model"""
    status: str
    count: str
    info: str
    infocode: str
    forecasts: list

@router.get("/api/weather_info")
async def get_weather_info(cityName: str = Query(..., description="Chinese city name, used to query weather information for the corresponding city")):
    """
    Get city weather information
    
    This endpoint queries weather information based on city name by calling the AMAP Weather API
    """
    try:
        # Log request data
        logging.info(f"Received weather query parameters: cityName={cityName}")
        
        # Validate city name length
        if len(cityName) <= 1:
            return {
                "status": "0",
                "count": "0",
                "info": "City name too short",
                "infocode": "10003",
                "forecasts": []
            }
        
        # Get the adcode corresponding to the city
        adcode = await get_city_adcode(cityName)
        if not adcode:
            return {
                "status": "0",
                "count": "0",
                "info": "Invalid city name",
                "infocode": "10003",
                "forecasts": []
            }
        
        # Call AMAP Weather API
        params = {
            "city": adcode,
            "key": AMAP_API_KEY,
            "extensions": AMAP_EXTENSIONS
        }
        
        async with aiohttp.ClientSession() as session:
            async with session.get(AMAP_WEATHER_API_URL, params=params) as response:
                if response.status == 200:
                    weather_data = await response.json()
                    logging.info(f"Retrieved weather data: {json.dumps(weather_data, indent=2)}")
                    return weather_data
                else:
                    error_text = await response.text()
                    logging.error(f"Weather API request failed: {response.status}, {error_text}")
                    return {
                        "status": "0",
                        "count": "0",
                        "info": f"Weather API request failed: {response.status}",
                        "infocode": "10002",
                        "forecasts": []
                    }
                
    except Exception as e:
        error_msg = f"Error getting weather information: {str(e)}\n{traceback.format_exc()}"
        logging.error(error_msg)
        return {
            "status": "0",
            "count": "0",
            "info": f"Error getting weather information: {str(e)}",
            "infocode": "10001",
            "forecasts": []
        }

async def get_city_adcode(city_name: str) -> Optional[str]:
    """
    Get the adcode corresponding to a city name
    
    Args:
        city_name: Chinese city name
        
    Returns:
        The city's adcode, or None if not found
    """
    try:
        # Get the path to the adcode mapping file
        current_dir = Path(__file__).parent
        adcode_file_path = current_dir / "amap_adcode.json"
        
        # Read the adcode mapping file
        with open(adcode_file_path, "r", encoding="utf-8") as f:
            adcode_map = json.load(f)
        
        # Find the adcode corresponding to the city
        # In the new JSON format, adcode_map is a list, with each element containing cityName and adcode fields
        for city_info in adcode_map:
            if city_info["cityName"].startswith(city_name) :
                return str(city_info["adcode"])
        return None
    except Exception as e:
        logging.error(f"Error getting city adcode: {str(e)}\n{traceback.format_exc()}")
        return None
