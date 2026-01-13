import asyncio
import json
import os
import signal
from functools import partial

from dotenv import load_dotenv
from websockets import ClientConnection
from websockets.asyncio.client import connect

from board import Board
from MockBoard import MockBoard
from ClientManager import ClientManager

load_dotenv()

# host_url = os.getenv('HARDWARE_SOCKET_URL', 'ws://localhost:8765')
host_url= 'ws://raspberrypi.local:8765'

state = {
    "on": False,
    "message": ""
}


async def process_message(message, board, websocket):
    global state
    print(f"led-sockets client: received message: {message}")
    # @todo: more refined handling
    try:
        payload = json.loads(message)
    except:
        return
    if payload['type'] != 'patch_hardware_state':
        return

    if (payload['attributes']['on']):
        state['on'] = True
        state['message'] = "The light and buzzer are on.  If I'm around it's annoying me."
        board.set_blue(True)
        board.buzz()
    else:
        state['on'] = False
        state['message'] = ""
        board.set_blue(False)
        board.stop_tone()

    payload = {
        "type": 'hardware_state',
        "id": '1',
        "attributes": state
    }
    await websocket.send(json.dumps(payload))


def on_button_press(board, websocket, button=None):
    global state
    board.stop_tone()
    board.set_blue(False)
    state['on'] = False
    state['message'] = "I turned it off"
    payload = {
        "type": 'hardware_state',
        "id": '',
        "data": state
    }
    asyncio.run(websocket.send(json.dumps(payload)))


def init_board(websocket: ClientConnection):
    print("led-sockets client: initializing board...")
    # board = Board()
    board = MockBoard()
    board.status_connected()
    board.add_button_press_handler(partial(on_button_press, board, websocket))
    return board


async def init_connection(websocket: ClientConnection):
    print("led-sockets client: initializing connection...")

    payload = {
        "type": "init_hardware",
        "relationships": {
            "hardware_state": {
                "data": {
                    "type": "hardware_state",
                    "attributes": state
                }
            }
        }
    }

    await websocket.send(json.dumps(payload))


async def init(websocket: ClientConnection):
    await init_connection(websocket)
    board = init_board(websocket)
    print("led-sockets client: awaiting messages")
    async for message in websocket:
        await process_message(message, board, websocket)


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
    load_dotenv()
    # server = ClientManager(
    #     # host=os.getenv('ECHO_SERVER_HOST', '0.0.0.0'),
    #     # port=int(os.getenv('ECHO_SERVER_PORT', '8765')),
    #     # handler=ServerHandler()
    # )
    # server.serve()
    print(f"led-sockets client: starting pid {os.getpid()}")
    asyncio.run(main())
