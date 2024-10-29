import logging
import asyncio

from fastapi import WebSocket, WebSocketDisconnect
from Service.common.data.websockets_managment import websocket_management
from Service.common.data.audio_receive_queue import audio_receive_queue
from Service.common.handle_disconnection import handle_disconnection
from Service.common.audio_transcription_processor import reset_everything, process_transcription_offline
from Service.common.data.transcription_context import transcription_context
from Service.config import *

async def transcription_logic(websocket: WebSocket):
    await websocket.accept()
    websocket_management.websockets.add(websocket)
    try:
        while True:
            data = await websocket.receive_bytes()
            await audio_receive_queue.audio_queue.put(data)
    
    except WebSocketDisconnect:
        handle_disconnection(websocket)
    
    except Exception as e:
        logging.error(f"WebSocket error: {e}")
        await websocket.close()


async def create_context_logic():
    asyncio.create_task(reset_everything())  # Assuming this is an async function
    summarized_message = await process_transcription_offline()
    transcription_context.transcription =  summarized_message.message
    return summarized_message.message, summarized_message.subject_conversation