import asyncio
import os

from dotenv import load_dotenv

from ClientHandler import ClientHandler
from ClientManager import ClientManager
from board import Board


async def main():
    loop = asyncio.get_running_loop()
    board = Board()
    handler = ClientHandler(
        board=board,
        loop=loop
    )
    server = ClientManager(
        host_url=os.getenv('HARDWARE_SOCKET_URL', 'ws://localhost:8765'),
        handler=handler
    )
    await server.serve()


if __name__ == "__main__":
    load_dotenv()
    asyncio.run(main())
