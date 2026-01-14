import asyncio
import datetime
import json
import os
import signal

from dotenv import load_dotenv
from websockets.asyncio.client import connect, ClientConnection

from ClientHandler import ClientHandler


# # @TODO:
# # -  [ ] A "reset" button on the board would be neat; resets state and reconnects to server

class ClientManager:
    LOG_PREFIX = 'led-sockets-client'
    CONNECTION_CLOSING_MESSAGE = 'I am dying'
    _connection: None | ClientConnection
    _host_url: str

    def __init__(self, host_url, handler):
        self._host_url = host_url
        self._handler = handler
        handler.setParent(self)
        self._connection = None
        self._tasks = []

    def _log(self, msg):
        timestamp = datetime.datetime.now().isoformat()
        print(f"{self.LOG_PREFIX} [{timestamp}] {msg}")

    async def _listen(self):
        """
        Listen to the websocket connection for new messages
        """
        self._log('Initialized.  Listening for messages...')
        if self._connection:
            async for message in self._connection:
                self._log(f'Server says: {message}  {self._connection.remote_address}')
                await self._handler.on_message(message, self._connection)
        else:
            raise Exception('Listen called without connection')

    async def handle_connection_closed(self):
        self._log('Server connection closed')
        self._handler.on_connection_closed()

    async def _initialize_connection(self):
        """
        Initialize websocket connection with identification payload
        """
        if not self._connection:
            raise Exception('Initializing non-existent connection')

        self._log('Initializing Connection')
        payload = {
            "type": "init_hardware",
            "relationships": {
                "hardware_state": {
                    "data": self._get_hardware_state()
                }
            }
        }
        await self._connection.send(json.dumps(payload))

    def _get_hardware_state(self):
        return self._handler.get_state()

    async def _shutdown(self, sig):
        """
        Perform a graceful shutdown.
        Cancel all active tasks within loop and notify connections of shutdown
        :param sig: The signal triggering the shutdown (SIGINT, SIGTERM
        :param tasks: The tasks to cancel for the shutdown
        """
        self._log(f"Shutdown signal received ({sig.name})")
        if (self._connection):
            self._log('Broadcasting impending death')
            await self._connection.send(self.CONNECTION_CLOSING_MESSAGE)
            await self._connection.close()
        for task in self._tasks:
            task.cancel()

        # @todo should not need to gather since it's already done in start_server
        # await asyncio.gather(*self._tasks, return_exceptions=True)

    async def _build_connection(self):
        """
        Build the websocket connection and queue initialization/listening
        @todo: refine exception handling if warranted
        @todo: wrap logic with while loop with a asyncio.sleep() to retry in the case network is lost
        """
        try:
            self._log('Establishing connection')
            async with connect(self._host_url) as websocket:
                self._log('Connected')
                self._handler.on_connected()
                self._connection = websocket
                await self._initialize_connection()
                self._handler.on_initialized()
                await self._listen()
                await self.handle_connection_closed()
        except OSError as e:
            self._log(f"Connection failed: {e}")
        except asyncio.CancelledError:
            pass
        finally:
            self._connection = None

    async def serve(self):
        """
        Create task wrapper for calling connection creation method
        Allows process to terminate gracefully on SIGINT and SIGKILL

        Registers shutdown handler upon signal
        """
        self._log(f"Starting (pid {os.getpid()})")
        loop = asyncio.get_running_loop()
        self._tasks = [
            asyncio.create_task(self._build_connection())
        ]
        for sig in (signal.SIGINT, signal.SIGTERM):
            loop.add_signal_handler(sig, lambda sig=sig: asyncio.create_task(self._shutdown(sig)))
        await asyncio.gather(*self._tasks)

    async def send_message(self, message):
        if self._connection:
            self._log(f"Sending message: {message}")
            await self._connection.send(message)
        else:
            self._log("Failed to send message: No active connection")


async def main():
    load_dotenv()
    server = ClientManager(
        host_url=os.getenv('HARDWARE_SOCKET_URL', 'ws://localhost:8765'),
        # host_url="ws://raspberrypi.local:8765",
        # handler=ClientHandler.createMocked(),
        handler=ClientHandler.create(),
    )
    await server.serve()


if __name__ == '__main__':
    asyncio.run(main())
