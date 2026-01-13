import datetime
import json

from MockBoard import MockBoard
from board import Board


class ClientHandler:
    LOG_PREFIX = 'led-sockets-handler'
    _state = {
        "on": False,
        "message": ""
    }

    def __init__(self, board):
        self._board = board

    def _log(self, msg):
        timestamp = datetime.datetime.now().isoformat()
        print(f"{self.LOG_PREFIX} [{timestamp}] {msg}")

    @classmethod
    def create(cls):
        return cls(Board())

    @classmethod
    def createMocked(cls):
        return cls(MockBoard())

    def on_connected(self):
        self._board.status_connected()
        pass

    def on_initialized(self):
        self._log('initialized')
        pass

    async def on_message(self, message, websocket):
        try:
            payload = json.loads(message)
        except:
            self._log('ignoring non-JSON message')
            return
        if payload['type'] == 'patch_hardware_state':
            if (payload['attributes']['on']):
                self._state['on'] = True
                self._state['message'] = "The light and buzzer are on.  If I'm around it's annoying me."
                self._board.set_blue(True)
                self._board.buzz()
            else:
                self._state['on'] = False
                self._state['message'] = ""
                self._board.set_blue(False)
                self._board.buzz(False)

        await websocket.send(json.dumps(self.get_state()))

    def get_state(self):
        return {
            "type": 'hardware_state',
            "attributes": self._state
        }

    def on_connection_closed(self):
        self._board.status_disconnected()
        pass
