import logging
import asyncio

from fastapi import WebSocket, WebSocketDisconnect
from Service.common.data.websockets_managment import websocket_manager
from Service.common.data.audio_receive_queue import audio_receive_queue
from Service.common.handle_disconnection import handle_disconnection
from Service.common.audio_transcription_processor import process_transcription_offline
from Service.common.data.transcription_context import transcription_context
from Service.config import *
from Service.common.audio_transcription_processor import AudioProcessor

async def transcription_logic(websocket: WebSocket):
    await websocket_manager.connect(websocket)
    audio_processor = AudioProcessor(websocket)
    try:
        while True:
            data = await websocket.receive_bytes()
            await websocket_manager.get_user_queue(websocket).put(data)
            asyncio.create_task(audio_processor.process_audio_queue())      
    except WebSocketDisconnect:
        websocket_manager.disconnect(websocket)
    
    except Exception as e:
        logging.error(f"WebSocket error: {e}")
        await websocket.close()


async def create_context_logic(audio):
    # asyncio.create_task(reset_everything())  # Assuming this is an async function
    summarized_message = await process_transcription_offline(audio)
    transcription_context.transcription =  summarized_message.message
    return summarized_message.message, summarized_message.subject_conversation