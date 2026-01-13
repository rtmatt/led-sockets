import os

from dotenv import load_dotenv

from ClientHandler import ClientHandler
from ClientManager import ClientManager

load_dotenv()

if __name__ == "__main__":
    load_dotenv()
    server = ClientManager(
        host_url=os.getenv('HARDWARE_SOCKET_URL', 'ws://localhost:8765'),
        handler=ClientHandler.create()
    )
    server.serve()
