import asyncio
import json
from abc import ABC, abstractmethod
from typing import Dict

from websockets.asyncio.server import ServerConnection
from websockets.client import ClientConnection

from ledsockets.dto.AbstractDto import DTOInvalidAttributesException, DTOInvalidPayloadException
from ledsockets.dto.HardwareClient import HardwareClient
from ledsockets.dto.HardwareState import HardwareState
from ledsockets.dto.PartialHardwareState import PartialHardwareState
from ledsockets.dto.TalkbackMessage import TalkbackMessage
from ledsockets.dto.UiClient import UiClient
from ledsockets.dto.UiMessage import UiMessage
from ledsockets.log.LogsConcern import Logs
from ledsockets.support.Message import Message, MessageException


# <editor-fold desc="Exceptions">
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


# </editor-fold>

class AbstractServerConnectionManager(ABC):
    @abstractmethod
    def handle(self, connection: ServerConnection):
        pass


class ServerConnectionManager(Logs, AbstractServerConnectionManager):
    """
    Manages business logic for a Server
    Handles connection management, routing and other business logic
    """
    LOGGER_NAME = 'ledsockets.server.handler'
    VALID_INIT_TYPES = ['init_client', 'init_hardware']

    def __init__(self):
        Logs.__init__(self)
        self._hardware_state: HardwareState = HardwareState()
        self._hardware_connection: HardwareClient | None = None
        self._client_connections: Dict[UiClient] = {}
        self._hardware_lock = asyncio.Lock()

    @property
    def is_hardware_connected(self):
        return self._hardware_connection is not None

    async def _handle_client_disconnect(self, client: UiClient):
        self._log(f'Client disconnected', 'info')
        client_id = client.id
        if client_id and client_id in self._client_connections:
            del self._client_connections[client_id]
        payload = UiMessage(f"Client {client.id} disconnected").toDict()
        await self._broadcast_to_clients(json.dumps([
            'ui_message',
            {"data": payload}
        ]), exclude_ids=[client.id])

    async def _on_talkback_message(self, message: Message, source: str):
        try:
            talkback = TalkbackMessage.from_message(message)
            self._log(f'{source} talkback message received: "{talkback.message}"', 'info')
        except DTOInvalidPayloadException as e:
            exception_message = f'Invalid talkback payload "{e}"'
            if source == 'Client':
                raise ClientMessageException(exception_message)
            else:
                raise HardwareMessageException(exception_message)

    async def _on_client_patch_hardware(self, message: Message, client: UiClient):
        self._log('Processing patch hardware state message', 'info')
        try:
            model = PartialHardwareState.from_message(message)
        except DTOInvalidAttributesException as e:
            raise ClientMessageException(str(e)) from e

        payload = model.toDict()
        payload['relationships'] = {
            "client": {
                "data": client.toDict()
            }
        }

        await self._send_message_to_hardware(json.dumps([
            'patch_hardware_state',
            {
                "data": payload
            }
        ]))

    async def _handle_client_message(self, raw_message: str, client: UiClient):
        self._log(f'Client message: {raw_message}', 'debug')

        try:
            message = Message.parse(raw_message)
        except MessageException as e:
            raise ClientMessageException(str(e)) from e

        match message.type:
            case 'patch_hardware_state':
                await self._on_client_patch_hardware(message, client)
            case 'talkback_message':
                await self._on_talkback_message(message, 'Client')
            case _:
                raise ClientMessageException(f"Unrecognized message type: \"{message.type}\"")

    async def _run_client_connection(self, client: UiClient):
        connection = client.connection
        async for message in connection:
            try:
                await self._handle_client_message(message, client)
            except ClientMessageException as e:
                self._log_exception(f"Ignoring invalid message: {e}")
                await self._send_error_message(f"Message had no effect ({e})", connection)

    async def _init_client_connection(self, client: UiClient):
        result_data = self._get_status()
        result_data['relationships']['ui_client'] = client.toDict()
        result_data['relationships']['talkback_messages'] = {
            "data": [TalkbackMessage("Hello, client!").toDict()]
        }
        result_data['relationships']['ui_message'] = {
            "data": UiMessage(f'You are connected!').toDict()
        }
        await client.connection.send(json.dumps([
            'client_init',
            {
                "data": result_data
            }
        ]))
        del result_data['relationships']["talkback_messages"]
        result_data['relationships']['ui_message'] = {
            "data": UiMessage(f'Client {client.id} joined').toDict()
        }
        await self._broadcast_to_clients(json.dumps([
            'client_joined',
            {
                "data": result_data
            }
        ]), exclude_ids=[client.id])

    def _record_client_connection(self, websocket: ServerConnection):
        self._log(f'Initializing client from {websocket.remote_address}', 'info')
        client = UiClient(str(websocket.id), websocket)
        self._client_connections[client.id] = client

        return client

    def _prune_dead_clients(self, results_by_id):
        """
        Following a sending loop, audit sending results for exceptions and purge the unsuccessful client connections
        """
        dead_clients = []
        for client_id, result in results_by_id:
            if isinstance(result, Exception):
                self._log(f'Client {client_id} connection exception: {result}', 'warning')
                dead_clients.append(client_id)

        for client_id in dead_clients:
            if client_id and client_id in self._client_connections:
                self._log(f'Dropping dead client connection {client_id}', 'info')
                # Close the connection just in case it's still active. This will drop any connections we can't successfully send to and remove it from tracking
                try:
                    client: UiClient | None = self._client_connections.get(client_id)
                    connection: ClientConnection | None = client.connection if client else None
                    if (connection):
                        # idempotent: closing it again is fine
                        connection.close()
                except Exception as e:
                    self._log_exception('Error dealing with dead client')
                del self._client_connections[client_id]

    async def _broadcast_to_clients(self, message, send_to_ids=None, exclude_ids=None):
        if not self._client_connections:
            return
        target_ids = send_to_ids if send_to_ids else list(self._client_connections.keys())
        if (exclude_ids):
            target_ids = list(set(target_ids) - set(exclude_ids))
        log_message = f"Broadcasting message to {len(target_ids)}/{len(self._client_connections)} client(s):"
        self._log(log_message, 'info')
        self._log(message, 'debug')
        if len(target_ids):
            tasks = [self._client_connections[cid].connection.send(message) for cid in target_ids]

            results = await asyncio.gather(*tasks, return_exceptions=True)
            self._prune_dead_clients(zip(target_ids, results))

    async def _send_message_to_hardware(self, message: str):
        if self._hardware_connection:
            self._log(f'Sending message to hardware: "{message}"', 'debug')
            await self._hardware_connection.connection.send(message)

    def _get_status(self):
        return {
            "type": "server_status",
            "id": "",
            "attributes": {
                "hardware_is_connected": self.is_hardware_connected
            },
            "relationships": {
                "hardware_state": {
                    "data": self._hardware_state.toDict()
                },
                "ui_clients": {
                    "data": [self._client_connections[cId].toDict() for cId in list(self._client_connections.keys())]
                },
                "hardware_client": {
                    "data": self._hardware_connection.toDict() if self._hardware_connection else None
                }
            }
        }

    async def _handle_hardware_disconnect(self):
        self._log(f'Hardware disconnected', 'info')
        self._hardware_connection = None
        self._hardware_state = HardwareState()
        self._log(f'Sending hardware disconnect signal to {len(self._client_connections)} client(s)', 'info')
        await self._broadcast_to_clients(json.dumps([
            'hardware_disconnected',
            {
                "data": self._get_status()
            }
        ]))

    async def _on_hardware_updated(self, message: Message):
        try:
            attributes = message.payload['data']['attributes']
            hardware_state = HardwareState.from_attributes(attributes)
        except DTOInvalidAttributesException as e:
            raise HardwareMessageException(f'{e}') from e
        except KeyError as e:
            raise HardwareMessageException(f'Key missing {e}') from e
        self._hardware_state = hardware_state
        self._log(f"Hardware state updated: {self._hardware_state.get_attributes()}", 'info')
        payload = hardware_state.toDict()
        uimessage = UiMessage('Temp test result')
        payload['relationships'] = {}
        payload['relationships']['ui_message'] = {"data": uimessage.toDict()}
        await self._broadcast_to_clients(json.dumps([
            'hardware_updated',
            {
                "data": payload
            }
        ]))

    async def _handle_hardware_message(self, raw_message: str):
        self._log(f'Hardware message: {raw_message}', 'debug')
        try:
            message = Message.parse(raw_message)
        except MessageException as e:
            raise HardwareMessageException(str(e)) from e
        except KeyError as e:
            raise HardwareMessageException(f"Payload key error: {e}") from e

        match message.type:
            case 'hardware_updated':
                await self._on_hardware_updated(message)
            case 'talkback_message':
                await self._on_talkback_message(message, 'Hardware')
            case _:
                raise HardwareMessageException(f'Unrecognized message type: "{message.type}"')

    async def _run_hardware_connection(self, hardware: HardwareClient):
        connection = hardware.connection
        async for message in connection:
            try:
                # @todo: pass connection param for consistency
                await self._handle_hardware_message(message)
            except HardwareMessageException as e:
                self._log(f"Ignoring invalid Hardware message: {e}", 'warning')
                await self._send_error_message(f"Message had no effect ({e})", connection)

    async def _init_hardware_connection(self, hardware: HardwareClient):
        connection = hardware.connection
        asyncio.create_task(connection.send(json.dumps([
            'talkback_message',
            {
                "data": TalkbackMessage("Hello, hardware").toDict()
            }
        ])))
        await self._broadcast_to_clients(json.dumps([
            'hardware_connected',
            {
                "data": self._get_status()
            }
        ]))

    def _record_hardware_connection(self, websocket: ServerConnection, message: Message):
        self._log(f'Initializing hardware from {websocket.remote_address}', 'info')
        try:
            attributes = message.payload['data']['attributes']
            hardware_state = HardwareState.from_attributes(attributes)
        except KeyError as e:
            raise InvalidHardwareInitPayloadException(f'Invalid attributes payload: "{e}"') from e
        except DTOInvalidAttributesException as e:
            raise InvalidHardwareInitPayloadException(f'{e}') from e

        self._hardware_connection = HardwareClient(str(websocket.id), websocket)
        self._hardware_state = hardware_state

        return self._hardware_connection

    async def _handle_hardware_connection(self, websocket: ServerConnection, message: Message):
        async with self._hardware_lock:
            if self.is_hardware_connected:
                raise HardwareAlreadyConnectedException()

            hardware = self._record_hardware_connection(websocket, message)
        try:
            await self._init_hardware_connection(hardware)
            await self._run_hardware_connection(hardware)
        finally:
            await self._handle_hardware_disconnect()

    async def _handle_client_connection(self, websocket: ServerConnection, message: Message):
        client = self._record_client_connection(websocket)
        try:
            await self._init_client_connection(client)
            await self._run_client_connection(client)
        finally:
            await self._handle_client_disconnect(client)

    async def _handle(self, websocket: ServerConnection):
        init_message = await websocket.recv()
        self._log(f'Init message received: {init_message}', 'debug')
        try:
            message = Message.parse(init_message)
            message_type = message.type
        except MessageException as e:
            raise InitPayloadInvalidException(str(e)) from e

        match message_type:
            case 'init_hardware':
                await self._handle_hardware_connection(websocket, message)
            case 'init_client':
                await self._handle_client_connection(websocket, message)
            case _:
                raise InitPayloadInvalidException(f'Invalid initialization type "{message_type}"')

    async def handle(self, websocket: ServerConnection):
        try:
            await self._handle(websocket)
        except InitPayloadInvalidException as e:
            message = str(e)
            self._log_exception(message)
            await self._send_error_message(message, websocket)
        except InvalidHardwareInitPayloadException as e:
            message = f'Hardware Init Error: {e}'
            self._log_exception('Hardware Init Error')
            await self._send_error_message(message, websocket)
        except HardwareAlreadyConnectedException as e:
            self._log('Hardware already connected; aborting connection', 'warning')
            await self._send_error_message('Hardware already connected.  Buh bye now.', websocket)

    async def _send_error_message(self, message: str, connection: ServerConnection):
        await connection.send(json.dumps([
            'error',
            {
                "errors": [{
                    "detail": message
                }]
            }
        ]))
