import os

from dotenv import load_dotenv

from AbstractBoard import AbstractBoard
from LogsConcern import Logs
from MockBoard import MockBoard
from board import Board


class BoardInterface:
    pass


class BoardController(Logs):
    LOG_PREFIX = 'led-socketsBoard Controller'

    def __init__(self, board: AbstractBoard):
        self._board = board
        self._state = {"buzzing": False, "blue": False, "red": False, "green": False, }

    def run(self):
        running = True
        while running:
            try:
                user_input = input('What do? (bu[z]zer, [b]lue, '
                                   '[r]ed, [g]reen '
                                   'b[u]tton, [t]one, [s]ilent'
                                   ', [q]uit): ').strip()
            except KeyboardInterrupt:
                print("\r")
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
                    running = False
                case _:
                    self._log('I don\'t know what that means')
        self._log('K byeeeee.')


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
    c.run()


if __name__ == "__main__":
    load_dotenv()
    main()
