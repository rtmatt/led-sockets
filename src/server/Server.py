import asyncio
import os
import signal
from functools import partial
from websockets.exceptions import ConnectionClosedOK, ConnectionClosedError

from dotenv import load_dotenv
from websockets.asyncio.server import serve

from Handler import Handler


class Server:
    LOG_PREFIX = "led-sockets server:"

    def __init__(self, host, port, handler):
        self._host = host
        self._port = port
        self._handler = handler.handle
        self._stop_event = asyncio.Event()
        self._shutting_down = False
        self._connections = set()
        pass

    def _log(self, message):
        print(f"{self.LOG_PREFIX} {message}")

    async def _close_connection(self, websocket):
        try:
            if not websocket.closed:
                try:
                    await websocket.send('Server shutting down')
                except Exception:
                    pass
                await websocket.close(1001)
        except Exception:
            pass

    async def _receive_connection(self, websocket):
        addr = websocket.remote_address
        self._connections.add(websocket)
        try:
            self._log(f"connection received: {addr}")
            await self._handler(websocket)
        except (ConnectionClosedOK, ConnectionClosedError):
            pass # Normal disconnection
        except Exception as e:
            self._log(f"Error handling connection from {adr}: {e}")
        finally:
            self._connections.discard(websocket)
            self._log(f"Connection closed for {addr}")

    def _shutdown(self, sig):
        if not self._shutting_down:
            self._shutting_down = True
            self._log(f'shutting down ({sig.name})...')
            self._stop_event.set()

    async def _serve(self):
        loop = asyncio.get_running_loop()
        for sig in (signal.SIGINT, signal.SIGTERM):
            loop.add_signal_handler(sig, partial(self._shutdown, sig))

        self._log(f"starting on {self._host}:{self._port} (pid {os.getpid()})")

        async with serve(self._receive_connection, self._host, self._port):
            await self._stop_event.wait()
            if self._connections:
                self._log(f"Closing {len(self._connections)} active connections")
                close_tasks = [self._close_connection(con) for con in list(self._connections)]
                await asyncio.gather(*close_tasks, return_exceptions=True)
        self._log("Server stopped")

    def serve(self):
        return asyncio.run(self._serve())


if __name__ == "__main__":
    load_dotenv()
    server = Server(
        host=os.getenv('ECHO_SERVER_HOST', '0.0.0.0'),
        port=int(os.getenv('ECHO_SERVER_PORT', '8765')),
        handler=Handler()
    )
    server.serve()
