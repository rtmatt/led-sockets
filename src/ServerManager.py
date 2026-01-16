import asyncio
import datetime
import os
import signal
from functools import partial

from dotenv import load_dotenv
from websockets.asyncio.server import ServerConnection
from websockets.asyncio.server import serve
from websockets.exceptions import ConnectionClosedOK, ConnectionClosedError

from ServerHandler import ServerHandler
from LogsConcern import Logs

class ServerManager(Logs):
    """
    Manages top-level server orchestration starting/stopping, opening/closing connections, system signal handling, etc
    offloads business logic to its handler
    """
    LOGGER_NAME = 'ledsockets.server.manager'
    SHUTDOWN_PAYLOAD = 'BYE FOREVER!'
    CLOSE_CODE = 1001
    KILL_MESSAGE = 'K byeeeeeeeeeeeeeeeeeee'

    def __init__(self, host: str, port: int, handler):
        Logs.__init__(self)
        self._host = host
        self._port = port
        self._handler = handler
        self._stop_event = asyncio.Event()
        self._shutting_down = False
        self._connections = set()

    @property
    def address(self):
        return f"{self._host}:{self._port}"

    def _record_connection(self, websocket: ServerConnection):
        self._log(f"Connection received from {websocket.remote_address}")
        self._connections.add(websocket)

    def _record_disconnect(self, websocket: ServerConnection):
        self._connections.discard(websocket)
        self._log(f"Connection dropped from {websocket.remote_address}")

    async def _close_connection(self, websocket: ServerConnection):
        if websocket.close_code is not None:
            return
        try:
            # Add a timeout so a single slow client doesn't hang the whole shutdown
            async with asyncio.timeout(2.0):
                await websocket.send(self.SHUTDOWN_PAYLOAD)
                await websocket.close(self.CLOSE_CODE)
        except Exception:
            pass

    async def _handle_connection(self, websocket):
        self._record_connection(websocket)
        try:
            await self._handler.handle(websocket)
        except (ConnectionClosedOK, ConnectionClosedError):
            pass
        except Exception as e:
            self._log(f"Exception unhandled by Handler: {e}")
        finally:
            self._record_disconnect(websocket)

    async def _disconnect_all(self):
        if self._connections:
            self._log(f"Closing active connections ({len(self._connections)})")
            tasks = [self._close_connection(conn) for conn in list(self._connections)]
            await asyncio.gather(*tasks, return_exceptions=True)

    def _trigger_shutdown(self, sig):
        if self._shutting_down:
            self._log(f"Already shutting down (received {sig.name})...")
            return
        self._shutting_down = True
        self._log(f"Shutting down (received {sig.name})...")
        self._stop_event.set()

    async def _run_server(self):
        async with serve(self._handle_connection, self._host, self._port) as server:
            await self._stop_event.wait()
            await self._stop_server()
        self._log(self.KILL_MESSAGE)

    async def _stop_server(self):
        await self._disconnect_all()

    async def serve(self):
        """
        Coordinate application lifecycle
        Register signal handlers to support graceful shutdowns
        """
        self._log(f"Starting on {self.address} (pid {os.getpid()})")
        loop = asyncio.get_running_loop()
        signals = (signal.SIGINT, signal.SIGTERM)

        for sig in signals:
            loop.add_signal_handler(sig, partial(self._trigger_shutdown, sig))
        try:
            await self._run_server()
        finally:
            for sig in signals:
                loop.remove_signal_handler(sig)
            self._log("Stopped")


async def main():
    load_dotenv()
    server = ServerManager(
        host=os.getenv('ECHO_SERVER_HOST', '0.0.0.0'),
        port=int(os.getenv('ECHO_SERVER_PORT', '8765')),
        handler=ServerHandler()
    )
    await server.serve()


if __name__ == '__main__':
    asyncio.run(main())
