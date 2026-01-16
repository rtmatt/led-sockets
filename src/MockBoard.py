import asyncio
import os
import sys
import threading

from AbstractBoard import AbstractBoard


async def ainput(prompt=''):
    """
    Get user input on separate thread to support killing process while waiting for input

    https://stackoverflow.com/questions/58493467/asyncio-keyboard-input-that-can-be-canceled
    :return:
    """
    loop = asyncio.get_event_loop()
    fut = loop.create_future()

    def _run():
        sys.stdout.write("\n")
        sys.stdout.write(f"{prompt}")
        line = sys.stdin.readline()
        loop.call_soon_threadsafe(fut.set_result, line)

    threading.Thread(target=_run, daemon=True).start()
    return await fut


class MockBoard(AbstractBoard):
    LOGGER_NAME = 'ledsockets.board.mock'

    def __init__(self):
        AbstractBoard.__init__(self)
        self._log('Starting up')  # @todo: see todo in concrete class  # self.status_on()  # self.status_disconnected()

    def cleanup(self):
        self._log('cleaning up')
        self.set_blue(False)
        self.set_green(False)
        self.set_red(False)
        self.stop_tone()

    def status_on(self):
        self._log('status on')
        self.set_green(True)

    def status_off(self):
        self._log('status off')
        self.set_green(False)

    def status_connected(self):
        self._log('status connected')
        self.set_red(False)

    def status_disconnected(self):
        self._log('status disconnected')
        self.set_red(True)

    def set_blue(self, value):
        self._log(f"blue {'on' if value else 'off'}")

    def set_green(self, value):
        self._log(f"green {'on' if value else 'off'}")

    def set_red(self, value):
        self._log(f"red {'on' if value else 'off'}")

    def play_tone(self, note="C5"):
        self._log(f'play tone {note}')

    def stop_tone(self):
        self._log('stop tone')

    def silent(self):
        self._log('silent')

    def buzz(self, on=True):
        if (on):
            self._log('buzz on')
        else:
            self._log('buzz off')

    async def run(self):
        self._log(f'running (pid:{os.getpid()})')

        async def prompt_input():
            running = True
            while running:
                inp = await ainput("What do? (b=button,q=quit): ")
                input_ = inp.strip()
                match input_:
                    case "b":
                        self._log('Simulating button press')
                        self.on_button_press(None)
                    case "q":
                        self._log('Fine then')
                        running = False
                    case _:
                        self._log(f'Ignoring unrecognized input "{input_}"')

        try:
            await prompt_input()
        except asyncio.CancelledError:
            self._log('Run canceled')

        self._log('BYEEEEEE')


if __name__ == "__main__":
    async def main():
        board = MockBoard()
        await board.run()


    asyncio.run(main())
