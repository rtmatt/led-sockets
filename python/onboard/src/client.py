import asyncio
from websockets.asyncio.client import connect

async def process(message):
    print(message)

async def main():
    async with connect("ws://localhost:8765") as websocket:
        async for message in websocket:
            await process(message)


if __name__ == "__main__":
    asyncio.run(main())
