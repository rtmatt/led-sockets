import asyncio
import json
from time import sleep
from websockets.asyncio.client import connect

from thing import Thing


async def process(message, thing):
    try:
        value = json.loads(message)["blue"]
        thing.set_blue(True if value == "on" else False)
        print(value)
    except:
        print('invalid request')



async def main():
    thing = Thing()
    sleep(1)
    async with connect("ws://localhost:8765") as websocket:
        thing.status_connected()
        async for message in websocket:
            await process(message, thing)


if __name__ == "__main__":
    asyncio.run(main())
