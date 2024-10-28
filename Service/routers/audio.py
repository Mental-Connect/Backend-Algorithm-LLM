import asyncio
import logging

from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from fastapi.responses import HTMLResponse

from Service.common.audio_receive_queue import audio_receive_queue
from Service.common.data.websockets_managment import websocket_management
from Service.common.handle_disconnection import *
from Service.common.http.context_request import ContextRequest
from Service.common.audio_transcription_process import *
from Service.config import *
from Service.common.data.transcription_context import transcription_context
from Service.common.http.context_response import ContextResponse

router = APIRouter()

@router.websocket("/audio-transcribe")
async def websocket_endpoint(websocket: WebSocket):
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


@router.post("/create-context")
async def create_context(request: ContextRequest):
    if request.command:
        asyncio.create_task(reset_everything())
        Summarized_message = await process_transcription_offline()
        transcription_context.transcription =  Summarized_message.message
        subject_identification_chat = Summarized_message.subject_conversation
        print(subject_identification_chat)
        # response_text = await subject_identification_processing()
        logging.info("Offline Context creation Completed")
    # Return a response after the wait
    return ContextResponse(Summarized_message= Summarized_message.message, response_text = subject_identification_chat)
