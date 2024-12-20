import json
import logging
import websockets

import io
import re 
from services.websocket_service import BaiduService
from services.offline_services import OfflineService
from Service.common.processing import baidu_processing, offline_processing
from Service.common.audio_saving import save_audio_to_wav
# Configure logger
logger = logging.getLogger(__name__)

async def handle_websocket_connection(websocket):
    """
    Handles the WebSocket connection from the client and communicates with the Baidu service.
    
    :param websocket: The WebSocket connection object for the client.
    :param path: The WebSocket request path.
    """
    print(f"New client connected: {websocket.remote_address}")

    # Create an instance of the BaiduService class
    # service = BaiduService()
    service = OfflineService()
    audio_data_buffer = io.BytesIO()

    # Establish connection to Baidu service
    # service.connect()

    try:
        async for message in websocket:
            print(f"received audio data from client, length: {len(message)}")

            # Send the audio data received from the client to the Baidu service
            audio_data_buffer.write(message)
            service.send_audio(message)

            # Retrieve response from the Baidu service (in this case, from the queue)
            response = service.fetch_messages_from_queue()
            if response:
                for res in response:
                    # formatted_response = await baidu_processing(res)
                    formatted_response = await offline_processing(res)
                    if formatted_response:
                        await websocket.send(json.dumps(formatted_response))
                        print(f"formatted response is:  {formatted_response}")
                    else:
                        print("No response received from model")

        audio_data_buffer.seek(0)  # Reset the buffer pointer to the beginning
        save_audio_to_wav(audio_data_buffer,websocket)

    except websockets.ConnectionClosed:
        print(f"Connection with {websocket.remote_address} closed.")
        service.send_finish()
        # Log if the WebSocket connection with the client is closed

