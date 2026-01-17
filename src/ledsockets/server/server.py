import asyncio
import os

from dotenv import load_dotenv

from ledsockets.server.ServerHandler import ServerHandler
from ledsockets.server.ServerManager import ServerManager


async def run_server():
    server = ServerManager(
        host=os.getenv('ECHO_SERVER_HOST', '0.0.0.0'),
        port=int(os.getenv('ECHO_SERVER_PORT', '8765')),
        handler=ServerHandler()
    )

    await server.serve()


def main():
    load_dotenv()
    asyncio.run(run_server())


if __name__ == "__main__":
    main()
