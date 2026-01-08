import os
import asyncio
import signal
from thing import Thing
from dotenv import load_dotenv
from websockets.asyncio.client import connect
import json

load_dotenv()

host_url = os.getenv('WEBSOCKET_HOST_URL', 'ws://localhost:8765')


async def process_message(message, thing):
    try:
        value = json.loads(message)["blue"]
        thing.set_blue(True if value == "on" else False)
        print(value)
    except:
        print('invalid request')


async def setup():
    try:
        thing = Thing()
        async with connect(host_url) as websocket:
            thing.status_connected()
            async for message in websocket:
                await process_message(message, thing);
    except asyncio.CancelledError:
        pass


async def shutdown(sig, tasks):
    print(f"LED-Sockets client: shutting down ({sig.name})...")
    for task in tasks:
        task.cancel()

    await asyncio.gather(*tasks, return_exceptions=True)
    print('Done.')


async def main():
    loop = asyncio.get_running_loop()
    tasks = [
        asyncio.create_task(setup())
    ]
    for sig in (signal.SIGINT, signal.SIGTERM):
        loop.add_signal_handler(sig, lambda sig=sig: asyncio.create_task(shutdown(sig, tasks)))

    await asyncio.gather(*tasks)


if __name__ == "__main__":
    print(f"LED-Sockets client: starting pid {os.getpid()}")
    asyncio.run(main())
