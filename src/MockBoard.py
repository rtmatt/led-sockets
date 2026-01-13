import datetime


class MockBoard:
    LOG_PREFIX = 'led-sockets-mock-board'

    def __init__(self):
        # self.green_led = LED(17)
        # self.blue_led = LED(12)
        # self.red_led = LED(21)
        # self.buzzer = TonalBuzzer(26, octaves=2)
        # self.button = Button(20)
        self.button_press_handlers = []
        self.button_release_handlers = []
        # self.button.when_pressed = self.on_button_press
        # self.button.when_released = self.on_button_release
        self._log('Board starting up')
        self.status_on()
        self.status_disconnected()

    def _log(self, msg):
        timestamp = datetime.datetime.now().isoformat()
        print(f"{self.LOG_PREFIX} [{timestamp}] {msg}")

    def cleanup(self):
        self._log('cleaning up')
        self.set_blue(False)
        self.set_green(False)
        self.set_red(False)
        self.stop_tone()

    def add_button_press_handler(self, handler):
        self._log('adding button press handler')
        self.button_press_handlers.append(handler)

    def add_button_release_handler(self, handler):
        self._log('adding button release handler')
        self.button_press_handlers.append(handler)

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
        print(f"set_blue: {value}")

    def set_green(self, value):
        print(f"set_green: {value}")

    def set_red(self, value):
        print(f"set_red: {value}")

    def play_tone(self, note="C5"):
        self._log(f'play tone {note}')

    def stop_tone(self):
        self._log('stop tone')

    def buzz(self, on=True):
        if (on):
            self._log('buzz on')
        else:
            self._log('buzz off')

    def on_button_press(self, button):
        for handler in self.button_press_handlers:
            handler(button)

    def on_button_release(self, button):
        for handler in self.button_release_handlers:
            handler(button)
