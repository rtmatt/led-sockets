from abc import ABC, abstractmethod

from LogsConcern import Logs


class AbstractBoard(ABC, Logs):
    def __init__(self):
        Logs.__init__(self)
        self.button_press_handlers = []
        self.button_release_handlers = []

    def on_button_release(self, button):
        for handler in self.button_release_handlers:
            handler(button)

    def on_button_press(self, button):
        for handler in self.button_press_handlers:
            handler(button)

    def add_button_press_handler(self, handler):
        self._log('adding button press handler')
        self.button_press_handlers.append(handler)

    def add_button_release_handler(self, handler):
        self._log('adding button release handler')
        self.button_press_handlers.append(handler)

    @abstractmethod
    def cleanup(self):
        pass

    @abstractmethod
    def status_on(self):
        pass

    @abstractmethod
    def status_off(self):
        pass

    @abstractmethod
    def status_connected(self):
        pass

    @abstractmethod
    def status_disconnected(self):
        pass

    @abstractmethod
    def set_blue(self, value):
        pass

    @abstractmethod
    def set_green(self, value):
        pass

    @abstractmethod
    def set_red(self, value):
        pass

    @abstractmethod
    def play_tone(self, note="C5"):
        pass

    @abstractmethod
    def stop_tone(self):
        pass

    @abstractmethod
    def buzz(self, on=True):
        pass

    def silent(self):
        pass

    @abstractmethod
    def status_connecting(self):
        pass
