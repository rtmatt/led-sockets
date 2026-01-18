import asyncio
import json
import os
import signal
from functools import partial

from dotenv import load_dotenv
from websockets.asyncio.client import connect, ClientConnection

from ledsockets.board.Board import Board
from ledsockets.board.MockBoard import MockBoard
from ledsockets.client.ClientEventHandler import ClientEventHandler
from ledsockets.contracts.MessageBroker import MessageBroker
from ledsockets.log.LogsConcern import Logs


class ClientConnectionError(Exception):
    """Represents an error when initializing or running a connection"""
    pass


class ClientMessageException(Exception):
    """Represents an issue processing a message"""
    pass


# # @TODO:
# # -  [ ] A "reset" button on the board would be neat; resets state and reconnects to server
# # - [ ] Following the previous, don't end process on a server connection break...sit and wait for button-based reconnect

class Client(Logs, MessageBroker):
    LOGGER_NAME = 'ledsockets.client.manager'
    CONNECTION_CLOSING_MESSAGE = 'I am dying'

    def __init__(self, host_url, handler: ClientEventHandler):
        Logs.__init__(self)
        self._host_url: str = host_url
        self._stop_event = asyncio.Event()
        self._shutting_down = False
        self._handler = handler
        self._handler.message_broker = self
        self._handler.event_loop = asyncio.get_running_loop()

        self._connection: None | ClientConnection = None
        self._log('Created', 'debug')

    async def send_message(self, message, connection=None):
        self._log(f"Sending message: {message}", 'debug')
        target = connection if connection else self._connection
        if not target:
            raise Exception('Unable to send message without a target')

        await target.send(message)

    async def _on_message(self, message, connection):
        if self._shutting_down:
            return

        self._log(f'Server says: {message}  {connection.remote_address}', 'debug')
        await self._handler.on_message(message, connection)

    async def _listen(self, connection: ClientConnection):
        self._log('Listening to connection', 'debug')
        async for message in connection:
            try:
                await self._on_message(message, connection)
            except Exception as e:
                raise ClientMessageException('Uncaught ClientEventHandler on_message error') from e
        if not self._shutting_down:
            self._log('Server closed the connection', 'info')

    async def _run_connection(self, connection):
        listen_task = asyncio.create_task(self._listen(connection))
        shutdown_task = asyncio.create_task(self._stop_event.wait())
        tasks, pending = await asyncio.wait(
            [listen_task, shutdown_task],
            return_when=asyncio.FIRST_COMPLETED,
        )
        # Re-raise any exceptions
        for t in tasks:
            self._log(f"Run connection result:{t.result()}", 'debug')

    async def _on_connection_closed(self):
        self._log('Processing closed connection', 'debug')
        # @todo: change named methods to external 'on' method as sole entry point (maybe not...sounds like it would be overloaded)
        self._handler.on_connection_closed(self._connection)
        self._connection = None

    async def _do_connection_init(self, connection):
        self._log('Processing new connection', 'debug')
        self._connection = connection
        self._handler.on_connection_open(connection)
        self._log('Sending init message', 'debug')
        payload = {
            "type": "init_hardware",
            "relationships": {
                "hardware_state": {
                    "data": self._handler.state_payload
                }
            }
        }
        await self.send_message(json.dumps(payload), connection)

    async def _on_connection_opened(self, connection):
        await self._do_connection_init(connection)
        self._handler.on_initialized(connection)

    async def _on_connection_pending(self):
        self._log('Opening connection', 'info')
        self._handler.on_connection_pending()

    async def _run_client(self):
        await self._on_connection_pending()
        try:
            async with connect(self._host_url) as websocket:
                try:
                    await self._on_connection_opened(websocket)
                except Exception as e:
                    raise ClientConnectionError('Error Initializing') from e

                try:
                    await self._run_connection(websocket)
                except Exception as e:
                    raise ClientConnectionError('Error running connection') from e

        except OSError as e:
            self._log_exception('Connection failed')
            raise e  # any exceptions at this point should kill the program since we have no reconnect loop
        except Exception as e:
            self._log_exception('Unspecified connection error')
            raise e  # any exceptions at this point should kill the program since we have no reconnect loop
        finally:
            # This finally hits whether the connection is closed on the server end (listen task ends) or killed locally (shutdown event resolves) or an exception happens
            await self._on_connection_closed()

    async def _trigger_shutdown(self, sig):
        if self._shutting_down:
            self._log(f"Already shutting down", 'debug')
            return
        self._log(f'[{sig.name}] Triggering shutdown', 'info')
        self._shutting_down = True

        if self._connection:
            self._log('Broadcasting impending death', 'debug')
            asyncio.create_task(self.send_message(self.CONNECTION_CLOSING_MESSAGE, self._connection))

        self._stop_event.set()

    def _handle_sigterm(self, sig):
        asyncio.create_task(self._trigger_shutdown(sig))

    async def run(self):
        self._log(f"Starting (pid {os.getpid()})", 'info')
        loop = asyncio.get_running_loop()
        signals = (signal.SIGINT, signal.SIGTERM)
        for sig in signals:
            loop.add_signal_handler(sig, partial(self._handle_sigterm, sig))
        try:
            await self._run_client()
        finally:
            for sig in signals:
                loop.remove_signal_handler(sig)
            self._log("Stopped", 'info')


async def run_client():
    MOCK_BOARD = os.getenv('MOCK_BOARD', 'false').lower() == 'true'
    if MOCK_BOARD:
        board = MockBoard()
    else:
        board = Board()

    board.run()

    handler = ClientEventHandler(
        board=board,
    )
    client = Client(
        host_url=os.getenv('HARDWARE_SOCKET_URL', 'ws://localhost:8765'),
        handler=handler
    )
    await client.run()


def main():
    load_dotenv()
    asyncio.run(run_client())


if __name__ == "__main__":
    main()
