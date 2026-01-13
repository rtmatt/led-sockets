import asyncio
import datetime
import json
import os
import signal
from typing import Union

from dotenv import load_dotenv
from websockets.asyncio.client import connect, ClientConnection


# # @TODO:
# # -  [ ] A "reset" button on the board would be neat; resets state and reconnects to server

class ClientManager:
    LOG_PREFIX = 'led-sockets-client'
    CONNECTION_CLOSING_MESSAGE = 'I am dying'
    _connection: Union[None | ClientConnection]
    _host_url: str

    def __init__(self, host_url):
        self._host_url = host_url
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
        else:
            raise Exception('Listen called without connection')

    async def handle_connection_closed(self):
        self._log('Server connection closed')

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
        return {
            "type": "hardware_state",
            "attributes": {
                "on": False  # @todo: get state from board
            }
        }

    async def _build_connection(self):
        """
        Build the websocket connection and queue initialization/listening
        """
        try:
            self._log('Establishing connection')
            async with connect(self._host_url) as websocket:
                self._log('Connected')
                self._connection = websocket
                await self._initialize_connection()
                await self._listen()
                await self.handle_connection_closed()
        except OSError as e:
            self._log(f"Connection failed: {e}")
        except asyncio.CancelledError:
            pass
        finally:
            self._connection = None

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

    async def _start_server(self):
        """
        Create task wrapper for calling connection creation method
        Allows process to terminate gracefully on SIGINT and SIGKILL

        Registers shutdown handler upon signal
        """
        self._log(f"Setting up context")
        loop = asyncio.get_running_loop()
        self._tasks = [
            asyncio.create_task(self._build_connection())
        ]
        for sig in (signal.SIGINT, signal.SIGTERM):
            loop.add_signal_handler(sig, lambda sig=sig: asyncio.create_task(self._shutdown(sig)))
        await asyncio.gather(*self._tasks)

    def serve(self):
        self._log(f"Starting (pid {os.getpid()})")
        asyncio.run(self._start_server())


if __name__ == '__main__':
    load_dotenv()
    server = ClientManager(
        "ws://raspberrypi.local:8765"  # os.getenv('HARDWARE_SOCKET_URL', 'ws://localhost:8765')
        # host=os.getenv('ECHO_SERVER_HOST', '0.0.0.0'),
        # port=int(os.getenv('ECHO_SERVER_PORT', '8765')),
        # handler=ServerHandler()
    )
    server.serve()
