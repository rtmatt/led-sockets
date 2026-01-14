import asyncio
import os

from dotenv import load_dotenv

from ClientHandler import ClientHandler
from ClientManager import ClientManager
from board import Board


async def main():
    server = ClientManager(
        host_url=os.getenv('HARDWARE_SOCKET_URL', 'ws://localhost:8765'),
        handler=ClientHandler(
            board=Board(),
            loop=asyncio.get_running_loop()
        )
    )
    await server.serve()


if __name__ == "__main__":
    load_dotenv()
    asyncio.run(main())
