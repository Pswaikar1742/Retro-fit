import asyncio
import websockets
import logging

logger = logging.getLogger(__name__)

class LogStreamingService:
    def __init__(self):
        self.clients = set()

    async def register_client(self, websocket):
        self.clients.add(websocket)
        logger.info(f"Client connected: {websocket.remote_address}")

    async def unregister_client(self, websocket):
        self.clients.remove(websocket)
        logger.info(f"Client disconnected: {websocket.remote_address}")

    async def broadcast_log(self, message: str):
        if self.clients:
            await asyncio.wait([client.send(message) for client in self.clients])

log_streaming_service = LogStreamingService()

async def log_streaming_endpoint(websocket, path):
    await log_streaming_service.register_client(websocket)
    try:
        async for message in websocket:
            logger.info(f"Received message from client: {message}")
    finally:
        await log_streaming_service.unregister_client(websocket)