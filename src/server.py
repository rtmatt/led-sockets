import asyncio
import os

from dotenv import load_dotenv

from ServerHandler import ServerHandler
from ServerManager import ServerManager


async def main():
    load_dotenv()
    server = ServerManager(
        host=os.getenv('ECHO_SERVER_HOST', '0.0.0.0'),
        port=int(os.getenv('ECHO_SERVER_PORT', '8765')),
        handler=ServerHandler()
    )
    await server.serve()


if __name__ == "__main__":
    asyncio.run(main())
