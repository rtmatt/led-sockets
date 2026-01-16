import asyncio
import datetime
import json
from asyncio import AbstractEventLoop


from LogsConcern import Logs

class ClientHandler(Logs):
    LOG_PREFIX = 'led-sockets-handler'
    LOGGER_NAME = 'ledsockets.client.handler'

    def __init__(self, board, loop):
        Logs.__init__(self)
        self._board = board
        self._loop: AbstractEventLoop = loop
        self._parent = None
        self._state = {
            "on": False,
            "message": ""
        }
        board.add_button_press_handler(self.on_button_press)

    def setParent(self, parent):
        # @todo: introducing an interface (ABC) would be better, but this is good enough for now
        if callable(getattr(parent, 'send_message', None)):
            self._parent = parent
        else:
            raise Exception('Invalid parent')

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
        # only process patch_hardware_state event
        if payload.get('type') == 'patch_hardware_state':
            try:
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
            except KeyError:
                # If there are any key errors, just ignore the message
                # @todo: In the Future, send a malformed json error to the single origin that this came from
                # I'm not doing that now because at this time sending a message would send it to all clients
                pass

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
            self._board.set_blue(False)
            self._state['on'] = False
            self._state['message'] = "I turned it off"
            if (self._parent):
                try:
                    await self._parent.send_message(json.dumps(self.get_state()))
                except Exception as e:
                    self._log(f"Error sending button press message: {e}")
        else:
            self._log("State is off; doing nothing")

    def on_button_press(self, button):
        if self._loop and self._loop.is_running():
            # Schedule the coroutine without blocking the hardware thread
            self._loop.call_soon_threadsafe(
                lambda: asyncio.create_task(self._on_button_press(button))
            )
        else:
            self._log("Cannot handle button press: Event loop is not running")
