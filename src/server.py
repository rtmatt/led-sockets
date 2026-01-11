import os
import signal
from dotenv import load_dotenv
import asyncio
from websockets.asyncio.server import serve

load_dotenv()

connections = set()


async def echo(websocket):
    async for message in websocket:
        print(message)
        for connection in connections:
            if connection is not websocket:
                print('sending to connection')
                await connection.send(message)
            else:
                print('skipping origin connection')


async def handler(websocket):
    connections.add(websocket)
    print(f"New connection ({len(connections)} clients connected)")
    try:
        await echo(websocket)
    finally:
        connections.remove(websocket)


async def setup():
    host = os.getenv('ECHO_SERVER_HOST', '0.0.0.0')
    port = os.getenv('ECHO_SERVER_PORT', '8765')
    print(f"led-sockets server: starting on {host}:{port}")
    try:
        async with serve(
                handler,
                host,
                int(port)
        ) as server:
            await server.serve_forever()
    except asyncio.CancelledError:
        pass


async def shutdown(sig, tasks):
    print(f"led-sockets server: shutting down ({sig.name})...")
    for task in tasks:
        task.cancel()

    await asyncio.gather(*tasks, return_exceptions=True)
    print("Done.")


async def main():
    loop = asyncio.get_running_loop()
    tasks = [
        asyncio.create_task(setup())
    ]
    for sig in (signal.SIGINT, signal.SIGTERM):
        loop.add_signal_handler(sig, lambda sig=sig: asyncio.create_task(shutdown(sig, tasks)))

    await asyncio.gather(*tasks)


if __name__ == "__main__":
    print(f"led-sockets server: starting pid {os.getpid()}")
    asyncio.run(main())
