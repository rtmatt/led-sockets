from gpiozero import LED, TonalBuzzer, Button


class Board:

    def __init__(self):
        self.green_led = LED(17)
        self.blue_led = LED(12)
        self.red_led = LED(21)
        self.buzzer = TonalBuzzer(26, octaves=2)
        self.button = Button(20)
        self.button_press_handlers = []
        self.button_release_handlers = []
        self.button.when_pressed = self.on_button_press
        self.button.when_released = self.on_button_release
        self.status_on()
        self.status_disconnected()

    def cleanup(self):
        print('led-sockets board: cleaning up')
        self.set_blue(False)
        self.set_green(False)
        self.set_red(False)
        self.stop_tone()

    def add_button_press_handler(self, handler):
        print('led-sockets board: adding button press handler')
        self.button_press_handlers.append(handler)

    def add_button_release_handler(self, handler):
        print('led-sockets board: adding button release handler')
        self.button_release_handlers.append(handler)

    def status_on(self):
        self.set_green(True)

    def status_off(self):
        self.set_green(False)

    def status_connected(self):
        self.set_red(False)

    def status_disconnected(self):
        self.set_red(True)

    def set_blue(self, value):
        if value:
            self.blue_led.on()
        else:
            self.blue_led.off()

    def set_green(self, value):
        if value:
            self.green_led.on()
        else:
            self.green_led.off()

    def set_red(self, value):
        if value:
            self.red_led.on()
        else:
            self.red_led.off()

    def play_tone(self, note="C5"):
        self.buzzer.play(note)

    def stop_tone(self):
        self.buzzer.stop()

    def buzz(self, on=True):
        if (on):
            self.play_tone('C3')
        else:
            self.stop_tone()

    def on_button_press(self, button):
        for handler in self.button_press_handlers:
            handler(button)

    def on_button_release(self, button):
        for handler in self.button_release_handlers:
            handler(button)
