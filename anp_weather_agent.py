import os
import sys
import asyncio
import logging
import traceback
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI, Request
import uvicorn
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse, FileResponse
from dotenv import load_dotenv

from utils.log_base import setup_logging, set_log_color_level
from api_router.router import router as agents_router
from api_router.did_auth_middleware import did_auth_middleware

# 加载环境变量
load_dotenv()

# 设置路径
current_script_path = os.path.abspath(__file__)
current_directory = os.path.dirname(current_script_path)
sys.path.append(current_directory)

app = FastAPI()

# 注册路由
app.include_router(agents_router)

# 打开跨域
origins = ["*"]

# 将CORS中间件添加到FastAPI应用中
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 添加DID认证中间件
app.middleware("http")(did_auth_middleware)

@app.get("/openapi.yaml", response_class=FileResponse)
async def get_openapi_yaml():
    return FileResponse(Path(current_directory) / "protocol" / "0.0.1.yaml")

@app.get("/logo.png", response_class=FileResponse)
async def get_logo():
    return FileResponse(Path(current_directory)  / "logo.png")

@app.get("/legal", response_class=HTMLResponse)
async def legal_information():
    return "提供消息发送和接收服务，支持用户之间的即时通讯。允许用户发送消息并查询未接收的消息，支持基于REST API的服务。"

@app.get("/ai-plugin.json", response_class=FileResponse)
async def get_baidu_plugin():
    return FileResponse(Path(current_directory) / "protocol" / "ai-plugin.json")

if __name__ == "__main__":
    # 初始化日志配置
    setup_logging()
    set_log_color_level(logging.INFO)
    g_server_port = 9870

    # ssl_certfile = "/home/code-ai-teacher/key/educopilot.net.pem"  # SSL 证书文件路径
    # ssl_keyfile = "/home/code-ai-teacher/key/educopilot.net.key"     # SSL 私钥文���路径
    # 如果是macOS系统
    if sys.platform == 'darwin':
        logging.info(f'启动服务，端口号：9000')
        uvicorn.run(app, host="0.0.0.0", port=9000)
    else:
        logging.info(f'启动服务，端口号：{g_server_port}')
        # uvicorn.run(app, host="0.0.0.0", port=g_server_port, ssl_certfile=ssl_certfile, ssl_keyfile=ssl_keyfile)
        uvicorn.run(app, host="0.0.0.0", port=g_server_port)
