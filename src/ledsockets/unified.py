import asyncio

from dotenv import load_dotenv

from ledsockets.client.client import run_client
from ledsockets.server.server import run_server


async def run_unified():
    await asyncio.gather(
        asyncio.create_task(run_server()),
        asyncio.create_task(run_client()),
    )


def main():
    load_dotenv()
    asyncio.run(run_unified())


if __name__ == "__main__":
    main()
