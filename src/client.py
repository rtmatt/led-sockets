import asyncio
import os

from dotenv import load_dotenv

from ClientHandler import ClientHandler
from ClientManager import ClientManager
from MockBoard import MockBoard
from board import Board


async def main():
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


if __name__ == "__main__":
    load_dotenv()
    asyncio.run(main())
