import os
import sys
import asyncio
import websockets
import uvicorn

from typing import Set

from funasr import AutoModel
from fastapi import FastAPI
from fastapi.responses import HTMLResponse

# Dynamically add the parent directory of the Service to sys.path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from handler.websocket_handler import handle_websocket_connection

from Service.routers import audio, chatbot, subject, audio_settings
from Service.common.audio_transcription_processor import *
from Service.common.data.audio_models import AudioModels
from Service.common.data.intensity_settings import IntensitySettings  
from Service.config import *

sys.path.append(os.path.join(os.path.dirname(__file__), '../'))

app = FastAPI()

# Include routers for audio, chatbot, subject, and audio settings
app.include_router(audio.router)
app.include_router(chatbot.router)
app.include_router(subject.router)
app.include_router(audio_settings.router)

# Root endpoint: Serve demo.html file as a response
@app.get("/")
async def get():
    demo_html = os.path.join(os.path.dirname(os.path.abspath(__file__)), "demo.html")
    with open(demo_html, encoding="utf-8") as file:
        content = file.read()
    return HTMLResponse(content)

# Startup and event handling logic

# Start audio queue processing on startup
@app.on_event("startup")
async def startup_event():
    # Initialize streaming, non-streaming, and full transcription models
    AudioModels.streaming_model = AutoModel(model=streaming_model, model_revision=streaming_model_revision)

    AudioModels.non_streaming_model = AutoModel(model=non_streaming_model, kwargs=kwargs, 
                                                vad_model=vad_model, vad_kwargs=vad_kwargs)
    
    AudioModels.full_transcription_model = AutoModel(
        model=non_streaming_model, kwargs=kwargs, punc_model=punc_model, vad_model=vad_model, 
        vad_kwargs=vad_kwargs, spk_model=spk_model, spk_model_revision=spk_model_revision
    )

    # Initialize intensity settings
    IntensitySettings.intensity_value = 0.0


# WebSocket service startup function
async def start_websocket_service():
    """Start the WebSocket service."""
    server = await websockets.serve(handle_websocket_connection, "localhost", 8001)
    print("WebSocket Service is running!")
    await server.wait_closed()

# Main function: Start both FastAPI and WebSocket services concurrently
async def main():
    # Start WebSocket service
    websocket_task = asyncio.create_task(start_websocket_service())

    # Start FastAPI service via Uvicorn
    uvicorn_task = asyncio.create_task(run_uvicorn())

    # Wait for all tasks to complete
    await asyncio.gather(websocket_task, uvicorn_task)

# Start the Uvicorn server
async def run_uvicorn():
    """Start the Uvicorn server."""
    config = uvicorn.Config(app, host="0.0.0.0", port=8000)
    server = uvicorn.Server(config)
    await server.serve()

# Program startup
if __name__ == "__main__":
    # Use asyncio.run() to start the event loop
    asyncio.run(main())
