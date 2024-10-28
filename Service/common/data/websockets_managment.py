from pydantic import BaseModel
from fastapi import WebSocket
from typing import Set

class WebsocketsManagement:
    """
    A class to manage WebSocket connections.

    Attributes:
        websockets (Set[WebSocket]): A set to store active WebSocket connections.
    """
    def __init__(self):
        self.websockets: Set[WebSocket] = set()

# Creating an instance of WebsocketsManagement
websocket_management = WebsocketsManagement()
