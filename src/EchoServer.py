import asyncio
import json
from typing import Set, Optional

from websockets import ServerConnection


class EchoServer:
    INITIAL_HARDWARE_STATE = {"on": False, "message": ""}
    LOG_PREFIX = "led-sockets server:"

    def __init__(self):
        self.connections: Set[ServerConnection] = set()
        self.hardware_connection: Optional[ServerConnection] = None
        self.client_connections: Set[ServerConnection] = set()
        self.hardware_state = self.INITIAL_HARDWARE_STATE.copy()

    @property
    def hardware_connected(self) -> bool:
        return self.hardware_connection is not None

    def _log(self, message):
        print(f"{self.LOG_PREFIX} {message}")

    async def handle_connection(self, websocket: ServerConnection):
        """Entry point for new websocket connections."""
        message = await websocket.recv()
        try:
            data = json.loads(message)
        except (json.JSONDecodeError, Exception):
            await self._send_error(websocket, "Invalid JSON format")
            return

        init_data = data.get("data")
        entity_type = init_data.get("entity_type") if init_data else None

        if data.get('type') != 'init' or not entity_type:
            self._log(f"Invalid init payload {message}")
            await self._send_error(websocket, "Invalid init payload")
            return

        if entity_type == 'hardware':
            await self._init_hardware(websocket, data)
        elif entity_type == 'client':
            await self._init_client(websocket)

    async def _send_error(self, websocket: ServerConnection, message: str):
        error_payload = {"type": "error", "data": {"message": message}}
        await websocket.send(json.dumps(error_payload))

    async def _init_hardware(self, websocket: ServerConnection, payload: dict):
        if self.hardware_connected:
            print(f'{self.LOG_PREFIX} hardware already connected. Ignoring')
            return

        hardware_state = payload.get("data", {}).get('hardware_state')
        if not hardware_state:
            self._log(f"Invalid init payload hardware_state {payload}")
            await self._send_error(websocket, "Invalid init payload hardware state")
            return

        self._log("new hardware connection")
        self.connections.add(websocket)
        self.hardware_connection = websocket
        self.hardware_state = hardware_state

        try:
            await self._broadcast_connection_status()
            await self._hardware_message_loop(websocket)
        finally:
            self._log('hardware disconnected')
            self.connections.discard(websocket)
            self.hardware_connection = None
            self.hardware_state = self.INITIAL_HARDWARE_STATE.copy()
            await self._broadcast_connection_status()

    async def _broadcast_connection_status(self):
        self._log('sending hardware connection status to clients')
        payload = {
            "type": "hardware_connection",
            "id": "",
            "data": {
                "is_connected": self.hardware_connected,
                "state": self.hardware_state
            }
        }
        await self._broadcast_to_clients(payload)

    async def _broadcast_to_clients(self, payload: dict):
        if not self.client_connections:
            return
        tasks = [client.send(json.dumps(payload)) for client in self.client_connections]
        await asyncio.gather(*tasks, return_exceptions=True)

    async def _init_client(self, websocket: ServerConnection):
        self.connections.add(websocket)
        self.client_connections.add(websocket)
        self._log(f"new client connection ({len(self.client_connections)} clients)")
        try:
            init_payload = {
                "type": 'client_connection_init',
                "id": "",
                "data": {
                    "hardware_is_connected": self.hardware_connected,
                    "hardware_state": self.hardware_state
                }
            }
            await websocket.send(json.dumps(init_payload))
            await self._client_message_loop(websocket)
        finally:
            print(f'{self.LOG_PREFIX} client disconnected')
            self.connections.discard(websocket)
            self.client_connections.discard(websocket)

    async def _hardware_message_loop(self, websocket: ServerConnection):
        async for message in websocket:
            try:
                self._log(f"hEcho \"{message}\"")
                payload = json.loads(message)
                if payload.get('type') == 'hardware_state':
                    self.hardware_state = payload.get('data')
                await self.broadcast_to_others(message, websocket)
            except json.JSONDecodeError:
                self._log("received invalid JSON from hardware")
            except Exception as e:
                self._log(f"error in hardware loop: {e}")

    async def _client_message_loop(self, websocket: ServerConnection):
        async for message in websocket:
            self._log(f"cEcho \"{message}\"")
            await self.broadcast_to_others(message, websocket)

    async def broadcast_to_others(self, message: str, source_socket: ServerConnection):
        tasks = [conn.send(message) for conn in self.connections if conn is not source_socket]
        if tasks:
            await asyncio.gather(*tasks, return_exceptions=True)
