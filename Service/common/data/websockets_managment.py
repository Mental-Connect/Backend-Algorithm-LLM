from pydantic import BaseModel
from fastapi import WebSocket
from typing import Set

class WebsocketsManagement:
    def __init__(self):
        self.websockets: Set[WebSocket] = set()

websocket_management = WebsocketsManagement()