import logging
from fastapi import WebSocket
from Service.common.data.websockets_managment import websocket_management


def handle_disconnection(websocket: WebSocket):
    websocket_management.websockets.remove(websocket)
    logging.info(f"Client disconnected")