import asyncio
import datetime
import json

from MockBoard import MockBoard
from board import Board


class ClientHandler:
    LOG_PREFIX = 'led-sockets-handler'

    def __init__(self, board):
        self._board = board
        self._parent = None
        self._state = {
            "on": False,
            "message": ""
        }
        # @todo: since this is initialized outside of any asyncio loop, the handler needs to
        #  start its own.  This results in a secondary asyncio loop that runs for the listener.
        #  Time will tell if this is a problem, but it smells off
        board.add_button_press_handler(self.on_button_press)

    def setParent(self, parent):
        # @todo: introducing an interface would be better, but this is good enough for now
        if callable(getattr(parent, 'send_message', None)):
            self._parent = parent
        else:
            raise Exception('Invalid parent')

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
        except json.JSONDecodeError:
            self._log('ignoring non-JSON message')
            return
        # @todo: more refined payload validation/checking/exception handling
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

    async def _on_button_press(self, button):
        self._log("Button press received")
        if (self._state['on']):
            self._board.buzz(False)
            self._state['on'] = False
            self._state['message'] = "I turned it off"
            if (self._parent):
                await self._parent.send_message(json.dumps(self.get_state()))
        else:
            self._log("State is off; doing nothing")

    def on_button_press(self, button):
        asyncio.run(self._on_button_press(button))
