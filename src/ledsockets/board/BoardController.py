import asyncio
import os
import time

from dotenv import load_dotenv

from ledsockets.board.AbstractBoard import AbstractBoard
from ledsockets.board.Board import Board
from ledsockets.board.MockBoard import MockBoard
from ledsockets.log.LogsConcern import Logs


class BoardController(Logs):
    LOGGER_NAME = 'ledsockets.board.controller'

    def __init__(self, board: AbstractBoard):
        Logs.__init__(self)
        self._board = board
        self._state = {"buzzing": False, "blue": False, "red": False, "green": False, }

    def run(self):
        self._log('Starting run')
        while True:
            try:
                user_input = input('What do? (bu[z]zer, [b]lue, '
                                   '[r]ed, [g]reen '
                                   'b[u]tton, [t]one, [s]ilent'
                                   ', [q]uit): ').strip()
            except (EOFError, KeyboardInterrupt):
                self._log('KBI/EOF', 'debug')
                break

            match user_input:
                case 'z':
                    self._state['buzzing'] = not self._state['buzzing']
                    self._board.buzz(self._state['buzzing'])
                case 'b':
                    self._state['blue'] = not self._state['blue']
                    self._board.set_blue(self._state['blue'])
                case 'r':
                    self._state['red'] = not self._state['red']
                    self._board.set_red(self._state['red'])
                case 'g':
                    self._state['green'] = not self._state['green']
                    self._board.set_green(self._state['green'])
                case 'u':
                    self._board.on_button_press(None)
                case 's':
                    self._board.silent()
                case 't':
                    try:
                        user_input = input('What tone?: ').strip()
                        self._board.play_tone(user_input)
                    except KeyboardInterrupt:
                        print("\r")
                        break
                    except ValueError as e:
                        print(e)
                case 'q':
                    break
                case _:
                    print('I don\'t know what that means')

        print('K byeeeee.')
        self._log('Run ended', 'info')

    async def run_lite(self):
        self._log('Starting run lite')
        while True:
            await asyncio.sleep(0.25)
            try:
                user_input = input("What do? (b[u]tton"
                                   ", [q]uit):"
                                   )
            except (EOFError, KeyboardInterrupt):
                self._log('KBI/EOF', 'debug')
                break

            match user_input:
                case 'u':
                    self._board.on_button_press(None)
                case 'q':
                    break
                case _:
                    print('I don\'t know what that means')

        print('K byeeeee.')
        self._log('Run ended', 'info')

    def run_lite_sync(self):
        self._log('Starting run lite')
        while True:
            time.sleep(0.25)
            try:
                user_input = input("What do? (b[u]tton"
                                   ", [q]uit):"
                                   )
            except (EOFError, KeyboardInterrupt):
                self._log('KBI/EOF', 'debug')
                break

            match user_input:
                case 'u':
                    self._board.on_button_press(None)
                case 'q':
                    break
                case _:
                    print('I don\'t know what that means')

        print('K byeeeee.')
        self._log('Run ended', 'info')


def main():
    def example_button_handler(button):
        print('button press heard')

    MOCK_BOARD = os.getenv('MOCK_BOARD', 'false').lower() == 'true'
    if MOCK_BOARD:
        board = MockBoard()
    else:
        board = Board()

    board.add_button_press_handler(example_button_handler)

    c = BoardController(board)
    # c.run()
    asyncio.run(c.run_lite())


if __name__ == "__main__":
    load_dotenv()
    main()
