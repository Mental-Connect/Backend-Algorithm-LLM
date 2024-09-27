import os
import sys
import asyncio
from typing import Set

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse

from Service.routers import audio, chatbot, subject
from Service.common.router_functions import *

sys.path.append(os.path.join(os.path.dirname(__file__), '../'))

app = FastAPI()

app.include_router(audio.router)
app.include_router(chatbot.router)
app.include_router(subject.router)

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
    asyncio.create_task(process_audio_queue())
