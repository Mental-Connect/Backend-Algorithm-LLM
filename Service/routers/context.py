import asyncio
from fastapi import APIRouter
from funasr import AutoModel
from fastapi import Depends
from Service.common.http.context_request import ContextRequest
from Service.common.session_manager import session_manager
from Service.common.audio_transcription_process import *
from Service.common.audio_models import AudioModels
from Service.config import *
import logging


router = APIRouter()

@router.post("/create-context")
async def create_context(request: ContextRequest):
    if request.command:
        await process_transcription_offline(AudioModels.non_streaming_model)  # Await the coroutine
        logging.info("Offline Context creation Completed")
    # Return a response after the wait
    return {"message": "Done"}