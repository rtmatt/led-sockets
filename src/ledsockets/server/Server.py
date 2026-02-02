import asyncio
import json
import os
import signal
from functools import partial

from dotenv import load_dotenv
from websockets.asyncio.server import ServerConnection
from websockets.asyncio.server import serve
from websockets.exceptions import ConnectionClosedOK, ConnectionClosedError

from ledsockets.dto.TalkbackMessage import TalkbackMessage
from ledsockets.log.LogsConcern import Logs
from ledsockets.server.ServerConnectionManager import ServerConnectionManager, AbstractServerConnectionManager


class Server(Logs):
    """
    Manages top-level server orchestration starting/stopping, opening/closing connections, system signal handling, etc
    offloads business logic to its handler
    """
    LOGGER_NAME = 'ledsockets.server.manager'
    SHUTDOWN_PAYLOAD = 'BYE FOREVER!'
    CLOSE_CODE = 1001
    KILL_MESSAGE = 'K byeeeeeeeeeeeeeeeeeee'

    def __init__(self, host: str, port: int, connection_manager: AbstractServerConnectionManager):
        Logs.__init__(self)
        self._host = host
        self._port = port
        self._connection_manager: AbstractServerConnectionManager = connection_manager
        self._stop_event = asyncio.Event()
        self._shutting_down = False
        self._connections = set()

    @property
    def address(self):
        return f"{self._host}:{self._port}"

    def _record_disconnect(self, websocket: ServerConnection):
        self._connections.discard(websocket)
        self._log(f"Connection dropped from {websocket.remote_address}", 'info')

    def _record_connection(self, websocket: ServerConnection):
        self._log(f"Connection received from {websocket.remote_address}", 'info')
        self._connections.add(websocket)

    async def _handle_connection(self, websocket):
        self._record_connection(websocket)
        try:
            await self._connection_manager.handle(websocket)
        except (ConnectionClosedOK, ConnectionClosedError):
            pass
        except Exception as e:
            self._log('Error in connection handler', 'error')
            # Raise exception so it can be handled by context manager
            raise e
        finally:
            self._record_disconnect(websocket)

    async def _close_connection(self, websocket: ServerConnection):
        if websocket.close_code is not None:
            return
        try:
            # Add a timeout so a single slow client doesn't hang the whole shutdown
            async with asyncio.timeout(2.0):
                await websocket.send(json.dumps([
                    'talkback_message',
                    {
                        "data": TalkbackMessage(self.SHUTDOWN_PAYLOAD).toDict()
                    }
                ]))
                await websocket.close(self.CLOSE_CODE)
        except Exception:
            self._log_exception('Exception during client disconnect')

    async def _disconnect_all(self):
        if self._connections:
            self._log(f"Closing active connections ({len(self._connections)})", 'info')
            tasks = [self._close_connection(conn) for conn in list(self._connections)]
            await asyncio.gather(*tasks, return_exceptions=True)

    async def _stop_server(self):
        await self._disconnect_all()

    async def _run_server(self):
        async with serve(self._handle_connection, self._host, self._port) as server:
            await self._stop_event.wait()
            await self._stop_server()
        self._log(self.KILL_MESSAGE, 'info')

    def _trigger_shutdown(self, sig):
        if self._shutting_down:
            self._log(f"Already shutting down (received {sig.name})...", 'warning')
            return
        self._log(f'[{sig.name}] Triggering shutdown', 'info')
        self._shutting_down = True
        self._stop_event.set()

    def _handle_sigterm(self, sig):
        self._trigger_shutdown(sig)

    async def serve(self):
        self._log(f"Starting on {self.address} (pid {os.getpid()})", 'info')
        loop = asyncio.get_running_loop()
        signals = (signal.SIGINT, signal.SIGTERM)
        for sig in signals:
            loop.add_signal_handler(sig, partial(self._handle_sigterm, sig))
        try:
            await self._run_server()
        finally:
            for sig in signals:
                loop.remove_signal_handler(sig)
            self._log("Stopped", 'info')


async def run_server():
    server = Server(
        host=os.getenv('ECHO_SERVER_HOST', '0.0.0.0'),
        port=int(os.getenv('ECHO_SERVER_PORT', '8765')),
        connection_manager=ServerConnectionManager()
    )

    await server.serve()


def main():
    load_dotenv()
    asyncio.run(run_server())


if __name__ == "__main__":
    main()
