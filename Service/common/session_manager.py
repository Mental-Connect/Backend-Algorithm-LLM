import asyncio
from collections import defaultdict
from typing import Set
from fastapi import WebSocket

# Constants
TRANSCRIPTION_KEY = "transcription"
class SessionManager:
    def __init__(self):
        self.transcriptions = []
        self.transcription_storage = {"transcription": " "}
        self.testing = []
        self.audio_queue = asyncio.Queue()
        self.student_id_info = ""
        self.database_data_saved = defaultdict(dict)
        self.active_websockets: Set[WebSocket] = set()
        self.previous_message_length = 0
        self.new_messgae_length = None
        self.counter: int = 0


session_manager = SessionManager()


