import asyncio

from websockets.asyncio.server import ServerConnection


class ServerHandler:
    LOG_PREFIX = 'led-sockets server:'
    DEFAULT_HARDWARE_STATE = {"on": False}

    SUPPORTED_CLIENTS = ['hardware', 'client']
    SOCKET_CODE_INVALID = 1003
    SOCKET_CODE_POLICY_ERROR = 1008

    def __init__(self):
        self._hardware_connection = None
        self._client_connections = set()
        self._hardware_state = self.DEFAULT_HARDWARE_STATE.copy()

    def _log(self, msg):
        print(f"{self.LOG_PREFIX} {msg}")

    async def handle(self, websocket: ServerConnection):
        # wait for initialization message from connection
        init_message = await websocket.recv()

        # determine the entity type from message information
        entity_type = 'hardware' if init_message == 'h' else 'client'

        # route initialization based on entity type
        if entity_type == 'hardware':
            await self._init_hardware(websocket, init_message)
        elif entity_type == 'client':
            await self._init_client(websocket, init_message)

    async def _init_hardware(self, websocket: ServerConnection, init_message):
        self._log(f'Initializing hardware from {websocket.remote_address}')

        # prevent hardware connections beyond initial one
        if (self._hardware_connection is not None):
            self._log('hardware already connected; aborting')
            raise Exception('hardware already connected')

        # store the hardware connection
        self._hardware_connection = websocket
        # set hardware state from init payload info
        self._hardware_state = {}

        # confirm init; @todo: don't need to await this for any reason, really
        await websocket.send("Hello, hardware")

        # let all connected clients know hardware has connected
        tasks = [client.send('Hardware connected [Info]') for client in list(self._client_connections)]
        await asyncio.gather(*tasks, return_exceptions=True)

        # send subsequent messages to clients.  fall through hardware init forwards message to clients
        async for message in websocket:
            self._log(f'Hardware message: {message}')
            # forward all messages to all clients
            self._log(f'sending hardware message to {len(self._client_connections)} clients')
            tasks = [client.send(message) for client in list(self._client_connections)]
            await asyncio.gather(*tasks, return_exceptions=True)

        # hardware disconnected
        self._log(f'Hardware disconnected')
        # remove the stored the hardware connection
        self._hardware_connection = None
        # reset hardware state
        self._hardware_state = self.DEFAULT_HARDWARE_STATE.copy()
        # compile async tasks to send disconnect to clients
        disconnect_tasks = [client.send('hardware disconnect') for client in self._client_connections]
        # wait for client messages to complete sending
        result = await asyncio.gather(*disconnect_tasks, return_exceptions=True)
        print(result)

    async def _init_client(self, websocket: ServerConnection, init_message):
        self._log(f'Initializing client from {websocket.remote_address}')
        # store the connection
        self._client_connections.add(websocket)
        # send state/status info to client for init (hardware connection status/state)
        await websocket.send("Hello, client. [Info]")
        # listen for messages from connection
        async for message in websocket:
            self._log(f'Client message: {message}')
            # client messages only send to hardware connection
            if self._hardware_connection:
                await self._hardware_connection.send(message)

        # client disconnected
        self._log(f'Client disconnected')
        # remove from clients on disconnect
        self._client_connections.discard(websocket)
