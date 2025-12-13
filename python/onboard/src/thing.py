class Thing:

    def __init__(self):
        # self.green_led = LED(17)
        # self.blue_led = LED(12)
        # self.red_led = LED(21)
        self.disconnected()

    def cleanup(self):
        print("Cleaning up")
        self.set_blue(False)
        self.set_green(False)
        self.set_red(False)

    def connected(self):
        print('setting connected state')

    def disconnected(self):
        print('setting disconnected state')

    def set_blue(self, value):
        print(f'Setting blue led to {value}')

    def set_green(self, value):
        print(f'Setting green led to {value}')

    def set_red(self, value):
        print(f'Setting red led to {value}')