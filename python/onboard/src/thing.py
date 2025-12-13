from gpiozero import LED
class Thing:

    def __init__(self):
        self.green_led = LED(17)
        self.blue_led = LED(12)
        self.red_led = LED(21)
        self.status_on()
        self.status_disconnected()

    def cleanup(self):
        print("Cleaning up")
        self.set_blue(False)
        self.set_green(False)
        self.set_red(False)

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