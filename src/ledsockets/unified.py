import asyncio

from dotenv import load_dotenv

from ledsockets.client.ClientManager import run_client
from ledsockets.server.ServerManager import run_server


async def run_unified():
    asyncio.create_task(run_client())
    await asyncio.gather(
        asyncio.create_task(run_server()),
    )


def main():
    load_dotenv()
    asyncio.run(run_unified())


if __name__ == "__main__":
    main()
