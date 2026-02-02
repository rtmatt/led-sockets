from ledsockets.dto.AbstractDto import AbstractDto
from ledsockets.dto.UiClient import UiClient


class ServerStatus(AbstractDto):
    TYPE = 'server_status'

    def __init__(self, hardware_is_connected: bool, id=''):
        super().__init__(id)
        self.hardware_is_connected = hardware_is_connected
        self._ui_client = None

    @property
    def ui_client(self):
        return self._ui_client

    @ui_client.setter
    def ui_client(self, val: UiClient):
        self._ui_client = val
        if (val):
            self.set_relationship('ui_client', val)
        else:
            self.remove_relationship('ui_client')


    def get_attributes(self):
        return {
            'hardware_is_connected': self.hardware_is_connected
        }
