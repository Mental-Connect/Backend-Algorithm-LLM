import os
import sys
import asyncio
import websockets
import uvicorn

from typing import Set

from funasr import AutoModel
from fastapi import FastAPI
from fastapi.responses import HTMLResponse

# 动态添加 Service 的父目录到 sys.path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from handler.websocket_handler import handle_websocket_connection

from Service.routers import audio, chatbot, subject, audio_settings
from Service.common.audio_transcription_processor import *
from Service.common.data.audio_models import AudioModels
from Service.common.data.intensity_settings import IntensitySettings  
from Service.config import *

sys.path.append(os.path.join(os.path.dirname(__file__), '../'))

app = FastAPI()

app.include_router(audio.router)
app.include_router(chatbot.router)
app.include_router(subject.router)
app.include_router(audio_settings.router)

@app.get("/")
async def get():
    demo_html = os.path.join(os.path.dirname(os.path.abspath(__file__)), "demo.html")
    with open(demo_html, encoding="utf-8") as file:
        content = file.read()
    return HTMLResponse(content)

# 其他启动和事件处理逻辑

# Start audio queue processing on startup
@app.on_event("startup")
async def startup_event():
    AudioModels.streaming_model = AutoModel(model=streaming_model, model_revision=streaming_model_revision)

    AudioModels.non_streaming_model = AutoModel(model=non_streaming_model,kwargs=kwargs, 
                                                vad_model=vad_model, vad_kwargs=vad_kwargs)
    
    AudioModels.full_transcription_model = AutoModel(model=non_streaming_model,kwargs=kwargs,punc_model =punc_model, vad_model=vad_model, 
                                                     vad_kwargs=vad_kwargs,spk_model=spk_model, 
                                                     spk_model_revision=spk_model_revision)
    IntensitySettings.intensity_value = 0.0



# WebSocket 服务启动函数
async def start_websocket_service():
    """启动 WebSocket 服务"""
    server = await websockets.serve(handle_websocket_connection, "localhost", 8765)
    print("WebSocket Service is running!")
    await server.wait_closed()

# 主函数：同时启动 FastAPI 和 WebSocket 服务
async def main():
    # 启动 WebSocket 服务
    websocket_task = asyncio.create_task(start_websocket_service())

    # 启动 FastAPI 服务（通过 uvicorn 启动）
    uvicorn_task = asyncio.create_task(run_uvicorn())

    # 等待所有任务完成
    await asyncio.gather(websocket_task, uvicorn_task)

# 启动 uvicorn 服务
async def run_uvicorn():
    """启动 Uvicorn 服务"""
    config = uvicorn.Config(app, host="0.0.0.0", port=8000)
    server = uvicorn.Server(config)
    await server.serve()

# 启动程序
if __name__ == "__main__":
    # 这里使用 asyncio.run() 来启动事件循环
    asyncio.run(main())