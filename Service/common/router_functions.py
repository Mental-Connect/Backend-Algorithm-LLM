import os
import sys
import tempfile
import logging

from fastapi import WebSocket

from Algorithm.audio_text_llm.service.audio_to_text import audio_to_text_model
from Service.common.session_manager import *

def handle_disconnection(websocket: WebSocket):
    session_manager.active_websockets.remove(websocket)
    full_transcription = " ".join(session_manager.transcriptions)
    session_manager.transcription_storage[TRANSCRIPTION_KEY] = full_transcription
    student_id = session_manager.student_id_info
    session_manager.database_data_saved[student_id]['Transcribed_Data'] = full_transcription
    logging.info(f"Client disconnected, full transcription: {full_transcription}")

async def process_audio_queue():
    while True:
        data = await session_manager.audio_queue.get()
        temp_file_path = save_temp_audio_file(data)
        if temp_file_path:
            await process_transcription(temp_file_path)

def save_temp_audio_file(data: bytes):
    try:
        with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as temp_file:
            temp_file.write(data)
            return temp_file.name
    except Exception as e:
        logging.error(f"Failed to save temporary file: {e}")
        return None

async def process_transcription(temp_file_path: str):
    try:
        message = audio_to_text_model(temp_file_path)
        session_manager.transcriptions.append(message)
        await send_transcription_to_clients(message)
    except Exception as e:
        logging.error(f"Error processing audio: {e}")
    finally:
        await remove_temp_file(temp_file_path)

async def send_transcription_to_clients(message: str):
    for websocket in session_manager.active_websockets:
        await websocket.send_text(message)

async def remove_temp_file(file_path: str):
    if os.path.exists(file_path):
        try:
            os.remove(file_path)
        except Exception as e:
            logging.error(f"Failed to remove temporary file: {e}")
