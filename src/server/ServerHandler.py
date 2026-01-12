import json

from websockets.asyncio.server import ServerConnection
from websockets.exceptions import ConnectionClosed


class ServerHandler:
    LOG_PREFIX = 'led-sockets server:'
    SUPPORTED_CLIENTS = ['hardware', 'client']

    def __init__(self):
        self._hardware_connection = None

    def _log(self, msg):
        print(f"{self.LOG_PREFIX} {msg}")

    async def handle(self, websocket: ServerConnection):
        try:
            message = await websocket.recv()
        except ConnectionClosed as e:
            return

        try:
            data = json.loads(message)
            type = data['type']
            entity_type = data['data']['entity_type']
            if type != 'init' or entity_type not in self.SUPPORTED_CLIENTS:
                raise Exception('Invalid type')
        except (json.JSONDecodeError, Exception):
            await websocket.close(1003, 'Invalid init payload')
            raise Exception('Invalid init payload')

        if entity_type == 'hardware':

            await self._init_hardware(websocket, data)
        elif entity_type == 'client':
            await self._init_client(websocket)

    async def _init_hardware(self, websocket: ServerConnection, data):
        if self._hardware_connection:
            await websocket.close(1008, 'Hardware already connected')
            raise Exception('Duplicate hardware registration')

        self._log("Initializing for hardware")
        self._hardware_connection = websocket

        async for message in websocket:
            print(message)

    async def _init_client(self, websocket: ServerConnection):
        self._log("Initializing for client")
        async for message in websocket:
            print(message)
