from fastapi import APIRouter, HTTPException, Request
from fastapi.responses import StreamingResponse
import json
import asyncio
import logging

# Create router
router = APIRouter()

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def stream_response(response: str):
    """Send response content to the client as a stream"""
    # Split the response into parts to simulate streaming output
    words = response.split()
    for word in words:
        yield f"data: {word}\n\n"
        await asyncio.sleep(0.1)  # Add some delay to make the stream more natural
    yield "data: [DONE]\n\n"


@router.post("/api/ask")
async def ask_weather_question(request: Request):
    """
    Process natural language questions about weather and return streaming answers
    """
    try:
        response = "Please use structured interface to query weather information, natural language queries are not supported yet, will be added later."

        # Return streaming response
        return StreamingResponse(
            stream_response(response), media_type="text/event-stream"
        )

    except json.JSONDecodeError:
        raise HTTPException(status_code=400, detail="Invalid JSON format")

    except Exception as e:
        logger.error(f"Error processing weather question: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")
