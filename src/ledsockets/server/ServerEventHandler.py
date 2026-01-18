import asyncio
import json

from websockets.asyncio.server import ServerConnection
from websockets.client import ClientConnection

from ledsockets.log.LogsConcern import Logs


class InvalidHardwareInitPayloadException(Exception):
    """Exception raised when hardware init payload is invalid"""
    pass


class HardwareAlreadyConnectedException(Exception):
    """Exception raised when hardware tries to connect with hardware already connected"""
    pass


class InitPayloadInvalidException(Exception):
    """Exception raised when primary init payload is invalid"""
    pass


class HardwareMessageException(Exception):
    """Exception raised when hardware message is invalid"""
    pass


class ClientMessageException(Exception):
    """Exception raised when client message is invalid"""
    pass


# TODO:
# - [ ] Pass simple messages as JSON.  Only do this if it becomes functionally prudent
class ServerEventHandler(Logs):
    LOGGER_NAME = 'ledsockets.server.handler'
    DEFAULT_HARDWARE_STATE = {"on": False}

    def __init__(self):
        Logs.__init__(self)
        self._hardware_state = None
        self._hardware_connection = None
        self._client_connections = {}
        self._hardware_lock = asyncio.Lock()

    @property
    def is_hardware_connected(self):
        return self._hardware_connection is not None

    def _log_exception(self, e: Exception, leading_message=''):
        log_message = leading_message if leading_message else str(e)
        if e.__cause__:
            log_message = f"{log_message} -- {e.__cause__.__class__.__name__}: {e.__cause__}"
        self._log(log_message)

    async def _handle_exception(self, e: Exception, websocket: ServerConnection):
        match e:
            case InitPayloadInvalidException():
                message = str(e)
                self._log_exception(e)
                await websocket.send(message)
            case HardwareAlreadyConnectedException():
                self._log('Hardware already connected; aborting connection')
                await websocket.send("Hardware already connected.  Buh bye now.")
            case InvalidHardwareInitPayloadException():
                message = f'Hardware Init Error: {e}'
                self._log_exception(e, message)
                await websocket.send(message)
            case HardwareMessageException():
                self._log_exception(e, f"Ignoring invalid message: {e}")
                await websocket.send(f"Message had no effect ({e})")
            case ClientMessageException():
                self._log_exception(e, f"Ignoring invalid message: {e}")
                await websocket.send(f"Message had no effect ({e})")
            case _:
                raise e

    async def handle(self, websocket):
        try:
            await self._handle(websocket)
        except Exception as e:
            await self._handle_exception(e, websocket)

    async def _handle(self, websocket: ServerConnection):
        init_message = await websocket.recv()
        self._log(f'Init message received: {init_message}')
        try:
            payload = json.loads(init_message)
            payload_type = payload['type']
            if payload_type not in ['init_client', 'init_hardware']:
                raise InitPayloadInvalidException(f'Invalid initialization type "{payload_type}"')
        except json.JSONDecodeError as e:
            raise InitPayloadInvalidException(f'Malformed initialization payload') from e
        except KeyError as e:
            raise InitPayloadInvalidException(f'Missing initialization payload key: {e}') from e

        # route initialization based on entity type
        if payload_type == 'init_hardware':
            async with self._hardware_lock:
                if self.is_hardware_connected:
                    raise HardwareAlreadyConnectedException()
                hardware = self._record_hardware_connection(websocket, payload)
            try:
                await self._init_hardware_connection(hardware)
                await self._run_hardware_connection(hardware)
            finally:
                await self._handle_hardware_disconnect()
        elif payload_type == 'init_client':
            client = self._record_client_connection(websocket)
            try:
                await self._init_client_connection(client)
                await self._run_client_connection(client)
            finally:
                await self._handle_client_disconnect(client)

    async def _run_hardware_connection(self, hardware):
        connection = hardware.get('connection')
        async for message in connection:
            try:
                await self._handle_hardware_message(message)
            except Exception as e:
                await self._handle_exception(e, connection)

    async def _run_client_connection(self, client):
        connection = client.get('connection')
        async for message in connection:
            try:
                await self._handle_client_message(message)
            except Exception as e:
                await self._handle_exception(e, connection)

    def _record_hardware_connection(self, websocket: ServerConnection, payload):
        self._log(f'Initializing hardware from {websocket.remote_address}')
        try:
            payload_type = payload['type']
            is_init = payload_type == 'init_hardware'
            if not is_init:
                raise InvalidHardwareInitPayloadException(f'Invalid event type "{payload_type}"')
            state = payload['relationships']['hardware_state']['data']['attributes']
            if not state:
                raise InvalidHardwareInitPayloadException('"hardware_state" data missing/invalid')
        except KeyError as e:
            raise InvalidHardwareInitPayloadException(f'Payload missing key: {e}') from e

        self._hardware_connection = {
            "id": websocket.id,
            "connection": websocket
        }
        self._hardware_state = state

        return self._hardware_connection

    def _record_client_connection(self, websocket: ServerConnection):
        self._log(f'Initializing client from {websocket.remote_address}')
        client = {
            "id": websocket.id,
            "connection": websocket
        }
        self._client_connections[client.get("id")] = client

        return client

    async def _init_hardware_connection(self, hardware):
        connection = hardware.get('connection')

        asyncio.create_task(connection.send("Hello, hardware"))

        payload = self.get_hardware_connection_payload()
        await self._broadcast_to_clients(json.dumps(payload))

    async def _init_client_connection(self, client):
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
        # Future-state in case client expands beyond websocket
        websocket = client.get('connection')
        await websocket.send(json.dumps(payload))

    async def _handle_hardware_message(self, message):
        self._log(f'Hardware says: {message}')

        try:
            payload = json.loads(message)
            payload_type = payload['type']
            attributes = payload['attributes']
            if not payload_type:
                raise HardwareMessageException("No payload type provided")
            if not attributes:
                raise HardwareMessageException("No payload attributes provided")
        except json.JSONDecodeError as e:
            raise HardwareMessageException("Non-JSON payload") from e
        except KeyError as e:
            raise HardwareMessageException(f"Payload key error: {e}") from e

        match payload_type:
            case 'hardware_state':
                # This is trusting of the hardware client.  However, we trust them more than ourselves to know what their state looks like.  At least for now
                self._hardware_state = attributes
                self._log(f"Hardware state updated: {self._hardware_state}")
            case _:
                raise HardwareMessageException(f"Unrecognized message type: \"{payload_type}\"")

        await self._broadcast_to_clients(message)

    async def _handle_client_message(self, message):
        self._log(f'Client message: {message}')

        try:
            payload = json.loads(message)
            payload_type = payload['type']
            if not payload_type:
                raise ClientMessageException("No payload type provided")
        except json.JSONDecodeError as e:
            raise ClientMessageException('Non-JSON payload') from e
        except KeyError as e:
            raise ClientMessageException(f"Payload key error: {e}") from e

        match payload_type:
            case 'patch_hardware_state':
                self._log('Passing message to hardware')
                await self._send_message_to_hardware(message)
            case _:
                raise ClientMessageException(f"Unrecognized message type: \"{payload_type}\"")

    async def _handle_hardware_disconnect(self):
        self._log(f'Hardware disconnected')
        self._hardware_connection = None
        self._hardware_state = None

        self._log(f'Sending hardware disconnect signal to {len(self._client_connections)} client(s)')
        payload = self.get_hardware_connection_payload()
        await self._broadcast_to_clients(json.dumps(payload))

    async def _handle_client_disconnect(self, client):
        self._log(f'Client disconnected')
        client_id = client.get('id')
        if client_id and client_id in self._client_connections:
            del self._client_connections[client_id]

    def get_hardware_connection_payload(self):
        return {"type": "hardware_connection",
                "attributes": {"is_connected": self._hardware_connection is not None
                               }, "relationships": {
                "hardware_state": {"data": {"type": "hardware_state", "attributes": self._hardware_state}}}}

    async def _broadcast_to_clients(self, message):
        if not self._client_connections:
            return

        self._log(f"Sending message to {len(self._client_connections)} client(s): {message}")
        client_ids = list(self._client_connections.keys())
        tasks = [self._client_connections[cid].get('connection').send(message) for cid in client_ids]

        results = await asyncio.gather(*tasks, return_exceptions=True)

        dead_clients = []
        for client_id, result in zip(client_ids, results):
            if isinstance(result, Exception):
                self._log(f'Client {client_id} connection exception: {result}')
                dead_clients.append(client_id)

        for client_id in dead_clients:
            if client_id and client_id in self._client_connections:
                self._log(f'Dropping dead client connection {client_id}')
                # Close the connection just in case it's still active. This will drop any connections we can't successfully send to internally and externally
                try:
                    connection: ClientConnection | None = self._client_connections.get(client_id)
                    if (connection):
                        # idempotent: closing it again is fine
                        connection.close()
                except Exception:
                    pass
                del self._client_connections[client_id]

    async def _send_message_to_hardware(self, message):
        if self._hardware_connection:
            await self._hardware_connection.get('connection').send(message)
