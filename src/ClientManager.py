import asyncio
import datetime
import json
import os
import signal

from dotenv import load_dotenv
from websockets.asyncio.client import connect


# # @TODO:
# # -  [ ] A "reset" button on the board would be neat; resets state and reconnects to server

class ClientManager:
    LOG_PREFIX = 'led-sockets-client'

    def __init__(self, host_url):
        self._host_url = host_url

    def _log(self, msg):
        timestamp = datetime.datetime.now().isoformat()
        print(f"{self.LOG_PREFIX} [{timestamp}] {msg}")

    async def _create_connection(self):
        try:
            self._log('Establishing connection')
            async with connect(self._host_url) as websocket:
                self._log('Connected')
                self._connection = websocket

                self._log('Sending init payload')
                payload = {
                    "type": "init_hardware",
                    "relationships": {
                        "hardware_state": {
                            "data": {
                                "type": "hardware_state",
                                "attributes": {
                                    "on": False  # @todo: get state from board
                                }
                            }
                        }
                    }
                }
                await self._connection.send(json.dumps(payload))

                self._log('Initialized.  Listening for messages...')
                async for message in self._connection:
                    self._log(f'Server says: {message}  {self._connection.remote_address}')

                self._log('Server connection closed')
        except OSError as e:
            self._log(f"Connection failed: {e}")
        except asyncio.CancelledError:
            print('cancel error caught')
        finally:
            self._connection = None

    async def shutdown(self, sig, tasks):
        self._log(f"Shutdown signal received ({sig.name})")
        if (self._connection):
            self._log('Broadcasting impending death')
            await self._connection.send('I am dying')
            await self._connection.close()
        for task in tasks:
            task.cancel()
        await asyncio.gather(*tasks, return_exceptions=True)

    async def _start_server(self):
        self._log(f"Setting up context")
        loop = asyncio.get_running_loop()
        tasks = [
            asyncio.create_task(self._create_connection())
        ]
        for sig in (signal.SIGINT, signal.SIGTERM):
            loop.add_signal_handler(sig, lambda sig=sig: asyncio.create_task(self.shutdown(sig, tasks)))
        await asyncio.gather(*tasks)

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
