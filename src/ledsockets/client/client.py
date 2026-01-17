import asyncio
import os

from dotenv import load_dotenv

from ledsockets.client.ClientHandler import ClientHandler
from ledsockets.client.ClientManager import ClientManager
from ledsockets.board.MockBoard import MockBoard
from ledsockets.board.Board import Board


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
