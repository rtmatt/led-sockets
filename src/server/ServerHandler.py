import asyncio
import json

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

        # @todo: try catch (json parse, not init, entity type invalid/absent
        payload = json.loads(init_message)
        # verify the payload represents an init event
        payload_type = payload['type']
        is_init = payload_type in ['init_client', 'init_hardware']

        # route initialization based on entity type
        if payload_type == 'init_hardware':
            await self._init_hardware(websocket, init_message)
        elif payload_type == 'init_client':
            await self._init_client(websocket, init_message)

    async def _init_hardware(self, websocket: ServerConnection, init_message):
        self._log(f'Initializing hardware from {websocket.remote_address}')

        # prevent hardware connections beyond initial one
        if (self._hardware_connection is not None):
            self._log('hardware already connected; aborting')
            raise Exception('hardware already connected')

        # @todo: try catch (json parse, not init, entity type invalid/absent
        # and ensure provided data is valid before proceeding
        payload = json.loads(init_message)
        # verify the payload represents an init event
        payload_type = payload['type']
        is_init = payload_type == 'init_hardware'
        state = payload['relationships']['hardware_state']['data']['attributes']

        # store the hardware connection
        self._hardware_connection = websocket
        # set hardware state from init payload info
        self._hardware_state = state

        # confirm init; @todo: don't need to await this for any reason, really
        await websocket.send("Hello, hardware")

        # payload for client notice of hardware connection
        payload = {
            "type": "hardware_connection",
            "attributes": {
                "is_connected": self._hardware_connection is not None  # true
            },
            "relationships": {
                "hardware_state": {
                    "data": {
                        "type": "hardware_state",
                        "attributes": self._hardware_state
                    }
                }
            }
        }

        # let all connected clients know hardware has connected
        tasks = [client.send(json.dumps(payload)) for client in list(self._client_connections)]
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

        # payload for client notice of hardware disconnection
        payload = {
            "type": "hardware_connection",
            "attributes": {
                "is_connected": self._hardware_connection is not None  # false
            },
            "relationships": {
                "hardware_state": {
                    "data": {
                        "type": "hardware_state",
                        "attributes": self._hardware_state  # should be reset
                    }
                }
            }
        }
        # compile async tasks to send disconnect to clients
        disconnect_tasks = [client.send(json.dumps(payload)) for client in self._client_connections]
        # wait for client messages to complete sending
        result = await asyncio.gather(*disconnect_tasks, return_exceptions=True)
        print(result)

    async def _init_client(self, websocket: ServerConnection, init_message):
        self._log(f'Initializing client from {websocket.remote_address}')
        # store the connection
        self._client_connections.add(websocket)

        # payload to client confirming init and providing initial state
        payload = {
            "type": "client_init",
            "attributes": {
                "hardware_is_connected": self._hardware_connection is not None,
                "message": "Hello, client!"
            },
            "relationships": {
                "hardware_state": {
                    "data": {
                        "type": "hardware_state",
                        "attributes": self._hardware_state
                    }
                }
            }
        }
        # send state/status info to client for init (hardware connection status/state)
        await websocket.send(json.dumps(payload))
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
