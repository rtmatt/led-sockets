import asyncio
import os

from dotenv import load_dotenv

from ledsockets.server.ServerHandler import ServerHandler
from ledsockets.server.ServerManager import ServerManager


async def main():
    server = ServerManager(
        host=os.getenv('ECHO_SERVER_HOST', '0.0.0.0'),
        port=int(os.getenv('ECHO_SERVER_PORT', '8765')),
        handler=ServerHandler()
    )
    await server.serve()


if __name__ == "__main__":
    load_dotenv()
    asyncio.run(main())
