import asyncio
import os

from dotenv import load_dotenv

from ledsockets.board.Board import Board
from ledsockets.board.MockBoard import MockBoard
from ledsockets.client.ClientHandler import ClientHandler
from ledsockets.client.ClientManager import ClientManager


async def run_client():
    MOCK_BOARD = os.getenv('MOCK_BOARD', 'false').lower() == 'true'

    if MOCK_BOARD:
        board = MockBoard()
    else:
        board = Board()

    board.run()

    handler = ClientHandler(
        board=board,
    )
    server = ClientManager(
        host_url=os.getenv('HARDWARE_SOCKET_URL', 'ws://localhost:8765'),
        handler=handler
    )
    await server.serve()


def main():
    load_dotenv()
    asyncio.run(run_client())


if __name__ == "__main__":
    main()
