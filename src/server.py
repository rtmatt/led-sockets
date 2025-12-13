import os
from dotenv import load_dotenv
import asyncio
from websockets.asyncio.server import serve

load_dotenv()

connections = set()


async def echo(websocket):
    async for message in websocket:
        print(message)
        for connection in connections:
            if connection is not websocket:
                print('sending to connection')
                await connection.send(message)
            else:
                print('skipping origin connection')


async def handler(websocket):
    connections.add(websocket)
    print(f"New connection ({len(connections)} clients connected)")
    try:
        await echo(websocket)
    finally:
        connections.remove(websocket)


async def main():
    async with serve(
            handler,
            os.getenv('SERVER_HOST', 'localhost'),
            int(os.getenv('SERVER_HOST', 'SERVER_PORT'))
    ) as server:
        await server.serve_forever()


if __name__ == "__main__":
    asyncio.run(main())
