from typing import  Optional
from fastapi import APIRouter,  Query
from pydantic import BaseModel
import aiohttp
import json
import traceback
import logging
from pathlib import Path
from config import AMAP_WEATHER_API_URL, AMAP_API_KEY

# 修改路由前缀，去掉 agents/travel/weather
router = APIRouter()

# 高德地图天气API参数
AMAP_EXTENSIONS = "all"

# 数据模型
class WeatherInfoRequest(BaseModel):
    """天气查询请求模型"""
    cityName: str

class WeatherInfoResponse(BaseModel):
    """天气查询响应模型"""
    status: str
    count: str
    info: str
    infocode: str
    forecasts: list

@router.get("/api/weather_info")
async def get_weather_info(cityName: str = Query(..., description="城市中文名称，用于查询对应城市的天气信息")):
    """
    获取城市天气信息
    
    该接口根据城市名称查询天气信息，通过调用高德地图天气API获取数据
    """
    try:
        # 记录请求数据
        logging.info(f"收到天气查询请求参数: cityName={cityName}")
        
        # 验证城市名称长度
        if len(cityName) <= 1:
            return {
                "status": "0",
                "count": "0",
                "info": "城市名称过短",
                "infocode": "10003",
                "forecasts": []
            }
        
        # 获取城市对应的adcode
        adcode = await get_city_adcode(cityName)
        if not adcode:
            return {
                "status": "0",
                "count": "0",
                "info": "城市名称无效",
                "infocode": "10003",
                "forecasts": []
            }
        
        # 调用高德地图天气API
        params = {
            "city": adcode,
            "key": AMAP_API_KEY,
            "extensions": AMAP_EXTENSIONS
        }
        
        async with aiohttp.ClientSession() as session:
            async with session.get(AMAP_WEATHER_API_URL, params=params) as response:
                if response.status == 200:
                    weather_data = await response.json()
                    logging.info(f"获取到天气数据: {json.dumps(weather_data, indent=2)}")
                    return weather_data
                else:
                    error_text = await response.text()
                    logging.error(f"天气API请求失败: {response.status}, {error_text}")
                    return {
                        "status": "0",
                        "count": "0",
                        "info": f"天气API请求失败: {response.status}",
                        "infocode": "10002",
                        "forecasts": []
                    }
                
    except Exception as e:
        error_msg = f"获取天气信息时出错: {str(e)}\n{traceback.format_exc()}"
        logging.error(error_msg)
        return {
            "status": "0",
            "count": "0",
            "info": f"获取天气信息时出错: {str(e)}",
            "infocode": "10001",
            "forecasts": []
        }

async def get_city_adcode(city_name: str) -> Optional[str]:
    """
    根据城市名称获取对应的adcode
    
    Args:
        city_name: 城市中文名称
        
    Returns:
        城市对应的adcode，如果未找到则返回None
    """
    try:
        # 获取adcode映射文件路径
        current_dir = Path(__file__).parent
        adcode_file_path = current_dir / "amap_adcode.json"
        
        # 读取adcode映射文件
        with open(adcode_file_path, "r", encoding="utf-8") as f:
            adcode_map = json.load(f)
        
        # 查找城市对应的adcode
        # 在新的JSON格式中，adcode_map是一个列表，每个元素包含cityName和adcode字段
        for city_info in adcode_map:
            if city_info["cityName"].startswith(city_name) :
                return str(city_info["adcode"])
        return None
    except Exception as e:
        logging.error(f"获取城市adcode时出错: {str(e)}\n{traceback.format_exc()}")
        return None
