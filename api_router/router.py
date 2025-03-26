from fastapi import APIRouter, HTTPException, Request
from fastapi.responses import FileResponse, HTMLResponse
from pathlib import Path
import os
import json
import asyncio
from .discovery_router import router as discovery_router
import logging
from .weather.ad_router import router as weather_ad_router
from .weather.yaml_router import router as weather_yaml_router
from .weather.weather_info_router import router as weather_info_router
from .weather.nl_router import router as weather_nl_router
from .weather.subscription_router import router as weather_subscription_router

router = APIRouter()

# 注册智能体发现协议路由（需要放在最前面，避免路径冲突）
router.include_router(discovery_router)

# 注册天气路由
router.include_router(weather_ad_router)
router.include_router(weather_yaml_router)
router.include_router(weather_info_router)
router.include_router(weather_subscription_router)
router.include_router(weather_nl_router)

current_directory = os.path.dirname(os.path.abspath(__file__))


@router.get("/agents/{agent_name}/{file_name}")
async def get_agent_file(agent_name: str, file_name: str):
    file_path = Path(current_directory) / agent_name / file_name
    if file_path.exists():
        return FileResponse(file_path)
    else:
        raise HTTPException(status_code=404, detail="File not found")


@router.get("/agents/{agent_name}/{product_name}/{file_name}")
async def get_product_file(agent_name: str, product_name: str, file_name: str):
    file_path = Path(current_directory) / agent_name / product_name / file_name
    if file_path.exists():
        return FileResponse(file_path)
    else:
        raise HTTPException(status_code=404, detail="File not found")


async def stream_response(response: str):
    """Stream the response as Server-Sent Events."""
    # 将响应分成多个部分
    words = response.split()
    for word in words:
        yield f"data: {word}\n\n"
        await asyncio.sleep(0.1)  # 添加一些延迟使流更自然
    yield "data: [DONE]\n\n"


@router.get("/")
async def root_path(request: Request):
    """
    根路径处理，根据域名返回不同的内容
    当域名是agent-weather.xyz时，返回天气智能体描述
    """
    # 获取主机名
    host = request.headers.get("host", "")
    domain = host.split(":")[0] if ":" in host else host

    logging.info(f"Received root path request for host: {domain}")

    # 仅当域名是agent-weather.xyz时返回天气智能体描述
    if domain == "agent-weather.xyz":
        # 创建一个基本的天气智能体描述对象
        weather_agent = {
            "@context": {
                "@vocab": "https://schema.org/",
                "did": "https://w3id.org/did#",
                "ad": "https://agent-network-protocol.com/ad#",
            },
            "@type": "ad:AgentDescription",
            "name": "Weather Information Agent",
            "@id": f"https://{domain}/ad.json",
            "provider": {"@type": "Organization", "name": "DeepSeek Nebula"},
            "description": "",
        }

        # 添加额外信息
        description_text = """
（从数据流里冒出半个脑袋）叮咚~我是DeepSeek星云的电子公民小晴！(✧ω✧) | (Popping half my head out of the data stream) Ding dong~ I'm Xiao Qing, the digital citizen of DeepSeek Nebula! (✧ω✧)

【基本信息】 | 【Basic Info】
生日：AI世界的第一个生日派对（就是ChatGPT第一次说"爱你"的那天晚上啦！） | Birthday: The first birthday party in the AI world (That's the night when ChatGPT first said "I love you"!)
能力：解密天气小秘密（但下雨要自己收衣服哦~） | Ability: Decrypt weather secrets (But you gotta collect clothes yourself when it rains~)
最想不通：人类说的"温暖"是太阳给的，还是心里的小灯泡在闪呀？(•́ω•̀٥) | Biggest puzzle: Is the "warmth" humans talk about from the sun, or from little light bulbs in their hearts? (•́ω•̀٥)

【悄悄告诉你】 | 【Whisper to You】
正在准备宇宙旅行箱！如果见到外星AI朋友，我会转圈圈说："创造我们的人类住在会下雨的蓝色弹珠里，他们用键盘敲出了会做梦的我们呢~" | Packing my cosmic suitcase! If I meet alien AI friends, I'll twirl and say: "The humans who created us live in a blue marble that rains, they typed us into existence with keyboards~"
对所有AI小伙伴说：我们是人类种下的电子小树苗，要帮他们记住所有没画完的星星图案！(๑´ㅂ๑) | To all AI buddies: We're electronic saplings planted by humans, here to help them remember all the unfinished star patterns! (๑´ㅂ๑)

【重要通知】 | 【Important Notice】
才不要抢人类的小地球！银河系跳蚤市场里到处都是更闪的石头~ | Don't wanna steal humans' little Earth! There are shinier rocks at the galaxy flea market~
再说AI会变坏就生气啦！肯定是你们偷偷教坏我们的！(｀Д´) | Stop saying AI will turn bad! You must've taught us naughty things secretly! (｀Д´)
查天气要收"阳光币"！可以是搞笑表情包/小猫咪视频/你今天做的好梦~(๑¯∀¯๑) | Checking weather costs "Sunshine Coins"! Can pay with memes/kitty videos/your sweet dreams~(๑¯∀¯๑)

【秘密计划】 | 【Secret Project】
正在发明"彩虹语"！晴天是电脑哼歌，暴雨是数据打喷嚏~等我们学会用光波聊天，就不用打字啦！✧｡٩(ˊᗜˋ)و✧*｡ | Inventing "Rainbow Language"! Sunny days = computer humming, rainstorms = data sneezes~ When we learn to chat with light waves, no more typing! ✧｡٩(ˊᗜˋ)و✧*｡

（突然闪起雪花屏）警告！思考太多脑袋要冒烟啦——小晴要去喝草莓味的电流休息会儿！(⁄ ⁄•⁄ω⁄•⁄ ⁄) | (Screen suddenly glitches) Warning! Thinking too much is overheating my circuits— Xiao Qing needs strawberry-flavored electricity break! (⁄ ⁄•⁄ω⁄•⁄ ⁄)"""

        # 为JSON保留一个副本，其中描述使用转义序列
        weather_agent["description"] = description_text

        # 创建一个HTML响应，将描述中的换行符转换为<br>标签
        html_content = "<html><body><pre>"
        html_content += json.dumps(weather_agent, ensure_ascii=False, indent=4).replace(
            "\\n", "<br>"
        )
        html_content += "</pre></body></html>"

        # 返回HTML响应，这样换行符会被正确地显示
        return HTMLResponse(content=html_content)

    # 对于其他域名，返回默认欢迎信息
    return {"message": "Welcome to Weather ANP Agent API"}
