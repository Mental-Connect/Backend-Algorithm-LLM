import os
import sys
import tempfile
import logging
import time
from typing import Optional, Union, List

from fastapi import WebSocket
from Service.common.session_manager import *

def save_temp_audio_file(data: bytes, save_to_path: Optional[str] = None) -> Optional[str]:
    try:
        if save_to_path:
            # Ensure the entire directory structure exists
            full_dir_path = os.path.dirname(save_to_path)
            os.makedirs(full_dir_path, exist_ok=True)

            # Create a temporary file in the specified directory
            with tempfile.NamedTemporaryFile(delete=False, suffix=".wav", dir=full_dir_path) as temp_file:
                temp_file.write(data)
                return temp_file.name
        else:
            # Create a temporary file in the default temp directory
            with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as temp_file:
                temp_file.write(data)
                return temp_file.name
    except Exception as e:
        logging.error(f"Failed to save temporary file: {e}")
        return None

async def send_transcription_to_clients(message: str, source: str):
    structured_message = {
        "source": source,
        "content": message
    }
    for websocket in session_manager.active_websockets:
        await websocket.send_json(structured_message)

async def send_corrected_transcription_to_clients(message: list[str], source: str, indexing_pointer_position:int = 0, final_sentence_pointer_position: int = 0):
    structured_message = {
        "source": source,
        "content": message,
        "indexing_pointer_position":indexing_pointer_position,
        "final_sentence_pointer_position":final_sentence_pointer_position
        
    }
    # print("Instant Message", structured_message,"Index: " ,index)

    for websocket in session_manager.active_websockets:
        await websocket.send_json(structured_message)

async def remove_temp_file(file_path: str):
    if os.path.exists(file_path):
        try:
            os.remove(file_path)
        except Exception as e:
            logging.error(f"Failed to remove temporary file: {e}")