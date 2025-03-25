from fastapi import APIRouter, HTTPException, Request
from fastapi.responses import StreamingResponse
import json
import asyncio
import logging

# 创建路由
router = APIRouter()

# 设置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def stream_response(response: str):
    """将响应内容以流的形式发送给客户端"""
    # 将响应分成多个部分，以模拟流式输出
    words = response.split()
    for word in words:
        yield f"data: {word}\n\n"
        await asyncio.sleep(0.1)  # 添加一些延迟使流更自然
    yield "data: [DONE]\n\n"

@router.post("/agents/travel/weather/api/ask")
async def ask_weather_question(request: Request):
    """
    处理用户关于天气的自然语言问题，并返回流式回答
    """
    try:
        # 解析请求数据
        data = await request.json()
        question = data.get("question")
        
        response = "请用结构化接口查询天气信息，暂不提供自然语言查询功能，后面会添加。"
        
        # 返回流式响应
        return StreamingResponse(
            stream_response(response),
            media_type="text/event-stream"
        )
    
    except json.JSONDecodeError:
        raise HTTPException(status_code=400, detail="无效的JSON格式")
    
    except Exception as e:
        logger.error(f"处理天气问题时发生错误: {str(e)}")
        raise HTTPException(status_code=500, detail=f"服务器内部错误: {str(e)}") 