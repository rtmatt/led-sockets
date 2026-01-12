import asyncio
import os
import signal
from functools import partial
from websockets.exceptions import ConnectionClosedOK, ConnectionClosedError
from dotenv import load_dotenv
from websockets.asyncio.server import serve

class Server:
    LOG_PREFIX = "led-sockets server:"
    SHUTDOWN_MSG = "Server shutting down"
    CLOSE_CODE_GOING_AWAY = 1001

    def __init__(self, host: str, port: int, handler):
        self._host = host
        self._port = port
        self._handler = handler.handle
        self._stop_event = asyncio.Event()
        self._shutting_down = False
        self._connections = set()

    @property
    def address(self):
        return f"{self._host}:{self._port}"

    def _log(self, message: str):
        print(f"{self.LOG_PREFIX} {message}")

    async def _close_connection(self, websocket):
        if websocket.closed:
            return
        try:
            await websocket.send(self.SHUTDOWN_MSG)
            await websocket.close(self.CLOSE_CODE_GOING_AWAY)
        except Exception:
            pass

    async def _handle_connection(self, websocket):
        addr = websocket.remote_address
        self._connections.add(websocket)
        self._log(f"Connection received: {addr}")
        try:
            await self._handler(websocket)
        except (ConnectionClosedOK, ConnectionClosedError):
            pass
        except Exception as e:
            self._log(f"Error handling connection from {addr}: {e}")
        finally:
            self._connections.discard(websocket)
            self._log(f"Connection closed for {addr}")

    def _trigger_shutdown(self, sig):
        if not self._shutting_down:
            self._shutting_down = True
            self._log(f"Shutting down (received {sig.name})...")
            self._stop_event.set()

    async def _run_server(self):
        loop = asyncio.get_running_loop()
        for sig in (signal.SIGINT, signal.SIGTERM):
            loop.add_signal_handler(sig, partial(self._trigger_shutdown, sig))

        self._log(f"Starting on {self.address} (pid {os.getpid()})")

        async with serve(self._handle_connection, self._host, self._port):
            await self._stop_event.wait()

            if self._connections:
                self._log(f"Closing {len(self._connections)} active connections")
                tasks = [self._close_connection(conn) for conn in list(self._connections)]
                await asyncio.gather(*tasks, return_exceptions=True)

        self._log("Server stopped")

    def serve(self):
        return asyncio.run(self._run_server())

if __name__ == "__main__":
    load_dotenv()
    server = Server(
        host=os.getenv('ECHO_SERVER_HOST', '0.0.0.0'),
        port=int(os.getenv('ECHO_SERVER_PORT', '8765')),
        handler=Handler()
    )
    server.serve()
