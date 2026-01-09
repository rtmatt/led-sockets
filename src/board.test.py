from time import sleep
from board import Board
from functools import partial

TEST_ACTIVE = True


def board_test():
    global TEST_ACTIVE
    board = Board()
    board.cleanup()
    board.buzz()
    sleep(0.5)
    board.set_green(True)
    board.play_tone('C4')
    sleep(0.1)
    board.set_blue(True)
    board.play_tone('E4')
    sleep(0.1)
    board.set_red(True)
    board.play_tone('G4')
    sleep(0.1)
    board.stop_tone()
    print('led-sockets board: holding until button press')
    sleep(0.5)
    board.buzz()

    def onpress(board, button=None):
        global TEST_ACTIVE
        TEST_ACTIVE = False
        board.stop_tone()

    board.add_button_press_handler(partial(onpress, board))

    while TEST_ACTIVE:
        sleep(0.25)


if __name__ == "__main__":
    try:
        print('led-sockets board: starting test...')
        board_test()
        print('led-sockets board: test complete')
    except KeyboardInterrupt:
        pass
