import asyncio
from collections import defaultdict
from typing import Set

from fastapi import FastAPI, WebSocket

# Constants
STATIC_DIR = "static"
TRANSCRIPTION_KEY = "transcription"
class SessionManager:
    def __init__(self):
        self.transcriptions = []
        self.transcription_storage = {TRANSCRIPTION_KEY: " "}
        self.audio_queue = asyncio.Queue()
        self.student_id_info = ""
        self.database_data_saved = defaultdict(dict)
        self.active_websockets: Set[WebSocket] = set()

session_manager = SessionManager()