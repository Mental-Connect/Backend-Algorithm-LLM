import logging
import websockets

from services.websocket_service import BaiduService

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
    baidu_service = BaiduService()

    # Establish connection to Baidu service
    baidu_service.connect()

    try:
        async for message in websocket:
            print(f"received audio data from client, length: {len(message)}")

            # Send the audio data received from the client to the Baidu service
            baidu_service.send_audio(message)

            # Retrieve response from the Baidu service (in this case, from the queue)
            response = baidu_service.fetch_messages_from_queue()

            # If the Baidu service returns data, forward it to the client
            if response:
                print(f"Received response from Baidu: {response}")
                await websocket.send(response)
            else:
                print("No response received from Baidu.")

    except websockets.ConnectionClosed:
        # Log if the WebSocket connection with the client is closed
        baidu_service.send_finish()  # Send finish frame to Baidu service when connection is closed
