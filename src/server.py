import os

from dotenv import load_dotenv

from ServerHandler import ServerHandler
from ServerManager import ServerManager

if __name__ == "__main__":
    load_dotenv()
    server = ServerManager(
        host=os.getenv('ECHO_SERVER_HOST', '0.0.0.0'),
        port=int(os.getenv('ECHO_SERVER_PORT', '8765')),
        handler=ServerHandler()
    )
    server.serve()
