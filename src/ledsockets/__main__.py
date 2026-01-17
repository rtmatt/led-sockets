import asyncio

from dotenv import load_dotenv

from ledsockets.client.client import main as client_main
from ledsockets.server.server import main as server_main


def ser():
    asyncio.run(server_main())


def cli():
    asyncio.run(client_main())


async def main():
    await asyncio.gather(
        server_main(),
        client_main()
    )


if __name__ == "__main__":
    load_dotenv()
    asyncio.run(main())
