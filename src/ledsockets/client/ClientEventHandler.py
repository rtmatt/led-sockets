import asyncio
import json
import os

from dotenv import load_dotenv

from ledsockets.board.AbstractBoard import AbstractBoard
from ledsockets.board.Board import Board
from ledsockets.board.BoardController import BoardController
from ledsockets.board.MockBoard import MockBoard
from ledsockets.contracts.MessageBroker import MessageBroker
from ledsockets.dto.AbstractDto import DTOInvalidPayloadException
from ledsockets.dto.ChangeDetail import ChangeDetail
from ledsockets.dto.HardwareState import HardwareState
from ledsockets.dto.PartialHardwareState import PartialHardwareState
from ledsockets.dto.TalkbackMessage import TalkbackMessage
from ledsockets.log.LogsConcern import Logs
from ledsockets.support.Message import Message, MessageException


class ServerMessageException(Exception):
    """Exception raised when a server message to hardware is invalid"""
    pass


class ClientEventHandler(Logs):
    """
    Handles events received by a hardware Client (connection)
    """
    LOGGER_NAME = 'ledsockets.client.handler'

    def __init__(self, board: AbstractBoard):
        Logs.__init__(self)
        self._state: HardwareState = HardwareState()
        self._board: AbstractBoard = board
        self._board.add_button_press_handler(self._on_board_button_press)
        self._connection = None
        self._message_broker: MessageBroker | None = None
        self._event_loop: asyncio.AbstractEventLoop | None = None
        self._log('Created', 'debug')

    def add_button_press_handler(self, callback):
        self._board.add_button_press_handler(callback)

    @property
    def event_loop(self):
        return self._event_loop

    @event_loop.setter
    def event_loop(self, value: asyncio.AbstractEventLoop):
        if value and not isinstance(value, asyncio.AbstractEventLoop):
            raise TypeError('Must be an asyncio.AbstractEventLoop')
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

    def _on_board_button_press(self, button=None):
        self._log('Button press received')
        if self._state.on:
            self._board.buzz(False)
            self._board.set_blue(False)
            self._state.on = False
            self._state.status_description = ""
            change_detail = ChangeDetail.from_attributes({
                "description": f"I turned it off at the source",
                "source_name": "I",
                "action_description": "turned it off at the source",
                "source_type": "board",
                "source_id": "",
                "old_value": True,
                "new_value": False,
            })
            try:
                payload = self._state
                payload.change_detail = change_detail
                asyncio.run_coroutine_threadsafe(
                    self._message_broker.send_message(json.dumps([
                        'hardware_updated',
                        {
                            "data": payload.toDict()
                        }
                    ])),
                    self._event_loop
                )
            except AttributeError as e:
                self._log(f'Sending update message failed {e}', 'warning')
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

    def on_auto_reconnect_pending(self):
        self._log('on_reconnect_waiting heard', 'debug')
        self._board.status_reconnect_pending()

    def on_auto_reconnect_failed(self):
        self._log('on_auto_reconnect_failed heard', 'debug')
        self._board.status_disconnected()

    async def _handle_message_exception(self, e: Exception, message):
        match e:
            case ServerMessageException():
                self._log(f'Ignoring invalid message ({e}): "{message}"', 'info')
            case _:
                raise e

    async def _on_talkback_message(self, message: Message):
        try:
            talkback = TalkbackMessage.from_message(message)
            self._log(f'Talkback message received: "{talkback.message}"', 'info')
        except DTOInvalidPayloadException as e:
            raise ServerMessageException(f'Invalid talkback payload "{e}"')

    async def _on_patch_hardware_state_message(self, message: Message):
        try:
            dto = PartialHardwareState.from_message(message)
            source = dto.source
        except KeyError as e:
            raise ServerMessageException(f'Invalid talkback payload "{e}"')

        original_value = self._state.on


        if dto.on:
            self._state.on = True
            self._state.status_description = "The light and buzzer are on.  If I'm around it's annoying me."
            self._board.set_blue(True)
            self._board.buzz()
            change_detail = ChangeDetail.from_attributes({
                "description": f"{source.name} turned it on",
                "source_name": source.name,
                "action_description": "turned it on",
                "source_type": source.type,
                "source_id": source.id,
                "old_value": original_value,
                "new_value": True,
            })

        else:
            self._state.on = False
            self._state.status_description = ""
            self._board.set_blue(False)
            self._board.buzz(False)
            change_detail = ChangeDetail.from_attributes({
                "description": f"{source.name} turned it off",
                "source_name": source.name,
                "action_description": "turned it off",
                "source_type": source.TYPE,
                "source_id": source.id,
                "old_value": original_value,
                "new_value": False,
            })

        payload: HardwareState = self._state
        payload.source = dto.source
        payload.change_detail = change_detail

        await self.message_broker.send_message(json.dumps([
            'hardware_updated',
            {
                "data": payload.toDict()
            }
        ]))

    async def _process_message(self, message: str):
        try:
            message = Message.parse(message)
            message_type = message.type
        except MessageException as e:
            raise ServerMessageException(str(e)) from e

        match message_type:
            case 'talkback_message':
                await self._on_talkback_message(message)
            case 'patch_hardware_state':
                await self._on_patch_hardware_state_message(message)
            case _:
                raise ServerMessageException(f'Unsupported payload type "{message_type}"')

    async def on_message(self, message, connection):
        self._log(f'Handling message: {message}', 'debug')
        try:
            await self._process_message(message)
        except Exception as e:
            await self._handle_message_exception(e, message)


async def main():
    MOCK_BOARD = os.getenv('MOCK_BOARD', 'false').lower() == 'true'
    if MOCK_BOARD:
        board = MockBoard()
    else:
        board = Board()

    board.run()

    class MockMessageBroker(MessageBroker):
        def send_message(self, message):
            print(f"Mock send: {message}")

    handler = ClientEventHandler(board=board, )
    handler.event_loop = asyncio.get_running_loop()
    handler.message_broker = MockMessageBroker()

    controller = BoardController(board)
    await controller.run_lite()


if __name__ == '__main__':
    load_dotenv()
    asyncio.run(main())
