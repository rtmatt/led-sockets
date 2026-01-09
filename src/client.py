import os
import asyncio
import signal
from websockets import ClientConnection
from board import Board
from dotenv import load_dotenv
from websockets.asyncio.client import connect
import json
from functools import partial

load_dotenv()

host_url = os.getenv('WEBSOCKET_HOST_URL', 'ws://localhost:8765')


async def process_message(message, board):
    print(f"led-sockets client: received message {message}")
    try:
        value = json.loads(message)["blue"]
        if (value == "on"):
            board.set_blue(True)
            board.buzz()
        else:
            board.set_blue(False)
            board.stop_tone()

        print(value)
    except:
        print('invalid request')


def on_button_press(board, websocket, button=None):
    board.stop_tone()
    board.set_blue(False)
    asyncio.run(websocket.send(json.dumps({
        "blue": "off"
    })))


async def init_board(websocket: ClientConnection):
    print("led-sockets client: initializing board...")
    board = Board()
    board.status_connected()
    board.add_button_press_handler(partial(on_button_press, board, websocket))
    print("led-sockets client: awaiting messages")
    async for message in websocket:
        await process_message(message, board)


async def setup():
    try:
        print(f"led-sockets client: connecting to {host_url}...")
        async with connect(host_url) as websocket:
            await init_board(websocket)

    except asyncio.CancelledError:
        pass


async def shutdown(sig, tasks):
    print(f"led-sockets client: shutting down ({sig.name})...")
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
    print(f"led-sockets client: starting pid {os.getpid()}")
    asyncio.run(main())
