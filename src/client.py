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

host_url = os.getenv('HARDWARE_SOCKET_URL', 'ws://localhost:8765')


async def process_message(message, board):
    print(f"led-sockets client: received message {message}")
    try:
        payload = json.loads(message)
        assert payload['type'] == 'change_state'
        if (payload['data']['is_on']):
            board.set_blue(True)
            board.buzz()
        else:
            board.set_blue(False)
            board.stop_tone()
    except:
        print('led-sockets client: invalid request')


def on_button_press(board, websocket, button=None):
    board.stop_tone()
    board.set_blue(False)
    payload = {
        "type": 'change_state',
        "id": '',
        "data": {
            "is_on": False
        }
    }
    asyncio.run(websocket.send(json.dumps(payload)))


def init_board(websocket: ClientConnection):
    print("led-sockets client: initializing board...")
    board = Board()
    board.status_connected()
    board.add_button_press_handler(partial(on_button_press, board, websocket))
    return board


async def init_connection(websocket: ClientConnection):
    print("led-sockets client: initializing connection...")
    await websocket.send(json.dumps({
        "type": "init",
        "id": "",
        "data": {
            "entity_type": 'hardware'
        }
    }))


async def init(websocket: ClientConnection):
    await init_connection(websocket)
    board = init_board(websocket)
    print("led-sockets client: awaiting messages")
    async for message in websocket:
        await process_message(message, board)


async def setup():
    try:
        print(f"led-sockets client: connecting to {host_url}...")
        async with connect(host_url) as websocket:
            await init(websocket)

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
