import os
import sys
import tempfile
import logging
import time
from typing import Optional

from fastapi import WebSocket
from Service.common.session_manager import *

def save_temp_audio_file(data: bytes, save_to_path: Optional[str] = None) -> Optional[str]:
    try:
        if save_to_path:
            # Ensure the entire directory structure exists
            full_dir_path = os.path.dirname(save_to_path)
            os.makedirs(full_dir_path, exist_ok=True)

            # Create a temporary file in the specified directory
            with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3", dir=full_dir_path) as temp_file:
                temp_file.write(data)
                return temp_file.name
        else:
            # Create a temporary file in the default temp directory
            with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as temp_file:
                temp_file.write(data)
                return temp_file.name
    except Exception as e:
        logging.error(f"Failed to save temporary file: {e}")
        return None

async def send_transcription_to_clients(message: str):
    for websocket in session_manager.active_websockets:
        await websocket.send_text(message)

async def remove_temp_file(file_path: str):
    if os.path.exists(file_path):
        try:
            os.remove(file_path)
        except Exception as e:
            logging.error(f"Failed to remove temporary file: {e}")