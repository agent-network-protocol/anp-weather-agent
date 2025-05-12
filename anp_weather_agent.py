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

# Load environment variables
load_dotenv()

# Set paths
current_script_path = os.path.abspath(__file__)
current_directory = os.path.dirname(current_script_path)
sys.path.append(current_directory)

app = FastAPI()

# Register routes
app.include_router(agents_router)

# Enable CORS
origins = ["*"]

# Add CORS middleware to FastAPI application
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Add DID authentication middleware
app.middleware("http")(did_auth_middleware)


@app.get("/openapi.yaml", response_class=FileResponse)
async def get_openapi_yaml():
    return FileResponse(Path(current_directory) / "protocol" / "0.0.1.yaml")


@app.get("/logo.png", response_class=FileResponse)
async def get_logo():
    return FileResponse(Path(current_directory) / "logo.png")


@app.get("/legal", response_class=HTMLResponse)
async def legal_information():
    return "Provides message sending and receiving services, supporting instant communication between users. Allows users to send messages and query unread messages, supporting REST API-based services."


@app.get("/ai-plugin.json", response_class=FileResponse)
async def get_baidu_plugin():
    return FileResponse(Path(current_directory) / "protocol" / "ai-plugin.json")


if __name__ == "__main__":
    # Initialize logging configuration
    setup_logging()
    set_log_color_level(logging.INFO)

    # If modifying the port, please confirm if AGENT_DESCRIPTION_JSON_DOMAIN needs to be updated
    g_server_port = 9870

    logging.info(f"Starting server on port: {g_server_port}")
    uvicorn.run(app, host="127.0.0.1", port=g_server_port)
