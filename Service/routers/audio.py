import asyncio
from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from fastapi.responses import HTMLResponse
from Service.common.session_manager import session_manager
import logging

router = APIRouter()

@router.websocket("/audio-transcribe")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    session_manager.active_websockets.add(websocket)
    try:
        while True:
            data = await websocket.receive_bytes()
            await session_manager.audio_queue.put(data)
            await websocket.send_text("Ping")
            await asyncio.sleep(10)  # 每10秒发送一次 Ping
    
    except WebSocketDisconnect:
        handle_disconnection(websocket)\
    
    except Exception as e:
        logging.error(f"WebSocket error: {e}")
        await websocket.close()
