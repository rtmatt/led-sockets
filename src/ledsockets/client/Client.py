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


class Client(Logs, MessageBroker):
    LOGGER_NAME = 'ledsockets.client.manager'
    CONNECTION_CLOSING_MESSAGE = 'I am dying'
    AUTO_RECONNECT_INTERVAL_CONFIG = [1, 60, 60 * 5, 60 * 10]

    def __init__(self, host_url, handler: ClientEventHandler):
        Logs.__init__(self)
        self._host_url: str = host_url
        self._stop_event = asyncio.Event()
        self._shutting_down = False
        self._handler = handler
        self._handler.message_broker = self
        self._event_loop: asyncio.AbstractEventLoop = asyncio.get_running_loop()
        self._handler.event_loop = asyncio.get_running_loop()

        self._connection: None | ClientConnection = None
        self._handler.add_button_press_handler(self._on_button_press)
        self._awaiting_reconnect = False
        self._reconnect_event: asyncio.Event = asyncio.Event()
        self._reconnect_intervals = self.AUTO_RECONNECT_INTERVAL_CONFIG.copy()
        self._log('Created', 'debug')

    async def _wait_manual_reconnect(self):
        await asyncio.wait([
            asyncio.create_task(self._reconnect_event.wait()),
            asyncio.create_task(self._stop_event.wait())
        ], return_when=asyncio.FIRST_COMPLETED)
        if (self._reconnect_event and self._reconnect_event.is_set()):
            self._log('Reconnecting...', 'info')
            await self._run_client()
        elif self._stop_event.is_set():
            self._log('Stop event heard; Abandon waiting for reconnect', 'info')

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
        # Cancel outstanding task
        for p in pending:
            p.cancel()
        # Re-raise any exceptions from completed tasks
        for t in tasks:
            if not t.cancelled() and t.exception():
                raise t.exception()

    async def _on_connection_closed(self):
        self._log('Processing closed connection', 'debug')
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
        # Reset active reconnect config on successful connections
        self._reconnect_intervals = self.AUTO_RECONNECT_INTERVAL_CONFIG.copy()
        await self._do_connection_init(connection)
        self._handler.on_initialized(connection)

    async def _on_connection_pending(self):
        self._log('Opening connection', 'info')
        self._handler.on_connection_pending()

    async def _handle_button_press(self):
        if (self._awaiting_reconnect):
            self._log('Button press: triggering reconnect', 'info')
            self._reconnect_event.set()
        else:
            self._log('Button press: ignored', 'info')

    def _on_button_press(self, button):
        self._log('Button press heard', 'debug')
        asyncio.run_coroutine_threadsafe(self._handle_button_press(), self._event_loop)

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
            # OSErrors arise from connection issues.  Fall through to reconnect loop
            self._log(f'Connection failed: {e}', 'error')
            # self._log_exception('Connection failed')
        except Exception as e:
            self._log_exception('Unspecified connection error')
            # Other exceptions at this point should be logged, then fall through to reconnect loop
        finally:
            # This finally hits whether the connection is closed on the server end (listen task ends) or killed locally (shutdown event resolves) or an exception happens
            await self._on_connection_closed()

        self._awaiting_reconnect = True
        self._reconnect_event.clear()
        # if shutting down (SIG), continue with shutdown
        if self._shutting_down:
            pass
        # Otherwise, attempt to reconnect according to remaining auto-reconnect configs
        elif len(self._reconnect_intervals):
            time = self._reconnect_intervals.pop(0)
            self._log(f'Awaiting Auto-reconnect attempt ({time}s; {len(self._reconnect_intervals)} remaining)', 'info')
            await asyncio.wait([
                asyncio.create_task(asyncio.sleep(time)),
                asyncio.create_task(self._stop_event.wait())
            ], return_when=asyncio.FIRST_COMPLETED)

            if (self._shutting_down):
                self._log('Shutdown heard during sleep; Abandoning reconnect', 'info')
            else:
                self._log('Auto-reconnect attempt', 'info')
                await self._run_client()

        else:
            # after x reconnect attempts, enter waiting loop (until button press)
            self._log('Awaiting manual reconnect', 'info')
            await self._wait_manual_reconnect()

    async def _trigger_shutdown(self, sig):
        if self._shutting_down:
            self._log(f"Already shutting down", 'debug')
            return
        self._log(f'[{sig.name}] Triggering shutdown', 'info')
        self._shutting_down = True

        if self._connection:
            self._log('Broadcasting impending death', 'debug')
            try:
                await asyncio.create_task(self.send_message(self.CONNECTION_CLOSING_MESSAGE, self._connection))
            except Exception as e:
                self._log(f"Failed to send shutdown message: {e}", 'warning')

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
