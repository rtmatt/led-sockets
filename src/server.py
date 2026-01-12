import asyncio
import os
import signal

from dotenv import load_dotenv
from websockets.asyncio.server import serve

from EchoServer import EchoServer


async def setup():
    """
    Set up the server
    Opens a websockets server with EchoServer.init_socket as the handler
    """
    host = os.getenv('ECHO_SERVER_HOST', '0.0.0.0')
    port = os.getenv('ECHO_SERVER_PORT', '8765')
    print(f"led-sockets server: starting on {host}:{port}")
    echo_server = EchoServer()
    try:
        async with serve(
                echo_server.handle_connection,
                host,
                int(port)
        ) as echo_server:
            await echo_server.serve_forever()
    except asyncio.CancelledError:
        pass


async def shutdown(sig, tasks):
    """
    :param sig: the shutdown signal
    :param tasks: the tasks to cancel
    Shut down the server.  Cancel all tasks
    """
    print(f"led-sockets server: shutting down ({sig.name})...")
    for task in tasks:
        task.cancel()

    await asyncio.gather(*tasks, return_exceptions=True)


async def main():
    """
    Coordinate application lifecycle
    Wrap setup within asyncio task which can be canceled when SIGINT or SIGTERM are heard
    This ensures the application can be stopped without error when monitored by something like supervisord
    """
    loop = asyncio.get_running_loop()
    tasks = [
        asyncio.create_task(setup())
    ]
    for sig in (signal.SIGINT, signal.SIGTERM):
        loop.add_signal_handler(sig, lambda sig=sig: asyncio.create_task(shutdown(sig, tasks)))

    await asyncio.gather(*tasks)


if __name__ == "__main__":
    load_dotenv()
    print(f"led-sockets server: starting pid {os.getpid()}")
    asyncio.run(main())
