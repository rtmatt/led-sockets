import asyncio
import os
import signal

from dotenv import load_dotenv
from websockets.asyncio.server import serve

from Handler import Handler


class Server:
    LOG_PREFIX = "led-sockets server:"

    def __init__(self, host, port, handler):
        self._host = host
        self._port = int(port)
        self._handler = handler.handle
        pass

    def _log(self, message):
        print(f"{self.LOG_PREFIX} {message}")

    async def _serve(self):
        loop = asyncio.get_running_loop()
        tasks = [asyncio.create_task(self._setup())]
        for sig in (signal.SIGINT, signal.SIGTERM):
            loop.add_signal_handler(sig, lambda sig=sig: asyncio.create_task(self._shutdown(sig, tasks)))

        await asyncio.gather(*tasks)

    def serve(self):
        return asyncio.run(self._serve())

    async def _shutdown(self, sig, tasks):
        self._log(f'shutting down ({sig.name})...')
        for task in tasks:
            task.cancel()

        await asyncio.gather(*tasks, return_exceptions=True)

    async def _handle_connection(self, websocket):
        self._log(f"connection received")
        return await self._handler(websocket)

    async def _setup(self):
        self._log(f"starting on {self._host}:{self._port} (pid {os.getpid()})")
        try:
            async with serve(self._handle_connection, self._host, self._port) as echo_server:
                await echo_server.serve_forever()
        except asyncio.CancelledError:
            pass


if __name__ == "__main__":
    load_dotenv()
    server = Server(
        host=os.getenv('ECHO_SERVER_HOST', '0.0.0.0'),
        port=os.getenv('ECHO_SERVER_PORT', '8765'),
        handler=Handler()
    )
    server.serve()
