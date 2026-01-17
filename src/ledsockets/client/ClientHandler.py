import asyncio
import json
import os

from dotenv import load_dotenv
from websockets import ServerConnection

from ledsockets.board.AbstractBoard import AbstractBoard
from ledsockets.board.BoardController import BoardController
from ledsockets.log.LogsConcern import Logs
from ledsockets.contracts.MessageBroker import MessageBroker
from ledsockets.board.MockBoard import MockBoard
from ledsockets.board.Board import Board


class ServerMessageException(Exception):
    """Exception raised when a server message to hardware is invalid"""
    pass


class ClientHandler(Logs):
    LOGGER_NAME = 'ledsockets.client.handler'
    DEFAULT_STATE = {
        "on": False,
        "message": ""
    }

    def __init__(self, board: AbstractBoard):
        Logs.__init__(self)
        self._state = self.DEFAULT_STATE.copy()
        self._board: AbstractBoard = board
        self._board.add_button_press_handler(self._on_board_button_press)
        self._connection = None
        self._message_broker: MessageBroker | None = None
        self._event_loop = None
        self._log('Created', 'debug')

    @property
    def event_loop(self):
        return self._event_loop

    @event_loop.setter
    def event_loop(self, value: MessageBroker):
        self._event_loop = value

    @property
    def message_broker(self):
        return self._message_broker

    @message_broker.setter
    def message_broker(self, value: MessageBroker):
        if not isinstance(value, MessageBroker):
            raise ValueError("Must be a MessageBroker")
        self._message_broker = value

    @property
    def state(self):
        return self._state.copy()

    @property
    def state_payload(self):
        return {"type": 'hardware_state', "attributes": self.state}

    async def _handle_message_exception(self, e: Exception, connection: ServerConnection):
        match e:
            case ServerMessageException():
                self._log(f'Ignoring invalid message: {e}','warning')
                # @todo: don't send a message.  The server and client won't stop telling each other their message
                #  wasn't JSON
                # await connection.send(f"Message had no effect ({e})")
            case _:
                raise e

    def _on_board_button_press(self, button=None):
        self._log('Button press received')
        if self._state['on']:
            self._board.buzz(False)
            self._board.set_blue(False)
            self._state['on'] = False
            self._state['message'] = "I turned it off"
            try:
                self._event_loop.call_soon_threadsafe(
                    lambda: asyncio.create_task(self._message_broker.send_message(json.dumps(self.state_payload)))
                )
            except AttributeError as e:
                self._log(f'Sending update message failed {e}', 'warning')
                # @todo: should the physical state reset? or cache/restore
        else:
            self._log("Button press ignored-- button is off", "info")

    def on_initialized(self, connection):
        self._log('on_initialized heard', 'debug')
        # technically connected earlier, but it's only ready after init
        self._board.status_connected()

    def on_connection_closed(self, connection):
        self._log('on_connection_closed heard', 'debug')
        self._connection = None
        self._board.status_disconnected()

    def on_connection_open(self, connection):
        self._log('on_connection_open heard', 'debug')
        self._connection = connection

    def on_connection_pending(self):
        self._log('on_connection_pending heard', 'debug')
        self._board.status_connecting()

    async def _process_message(self, message: str, connection):
        try:
            payload = json.loads(message)
            payload_type = payload['type']
            if payload_type != 'patch_hardware_state':
                raise ServerMessageException(f'Unsupported payload type "{payload_type}"')
            on = payload['attributes']['on']
        except json.JSONDecodeError as e:
            raise ServerMessageException(f'Non-JSON payload') from e
        except KeyError as e:
            raise ServerMessageException(f"Payload key error: {e}") from e

        if on:
            self._state['on'] = True
            self._state['message'] = "The light and buzzer are on.  If I'm around it's annoying me."
            self._board.set_blue(True)
            self._board.buzz()
        else:
            self._state['on'] = False
            self._state['message'] = ""
            self._board.set_blue(False)
            self._board.buzz(False)

        await connection.send(json.dumps(self.state_payload))

    async def on_message(self, message, connection):
        self._log(f'Handling message: {message}', 'debug')
        try:
            await self._process_message(message, connection)
        except Exception as e:
            await self._handle_message_exception(e, connection)


async def main():
    MOCK_BOARD = os.getenv('MOCK_BOARD', 'false').lower() == 'true'
    if MOCK_BOARD:
        board = MockBoard()
    else:
        board = Board()

    board.run()

    handler = ClientHandler(board=board, )

    controller = BoardController(board)
    await controller.run_lite()


if __name__ == '__main__':
    load_dotenv()
    asyncio.run(main())
