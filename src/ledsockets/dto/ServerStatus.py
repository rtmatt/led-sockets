from ledsockets.dto.AbstractDto import AbstractDto


class ServerStatus(AbstractDto):
    TYPE = 'server_status'

    def __init__(self, hardware_is_connected: bool, id=''):
        super().__init__(id)
        self.hardware_is_connected = hardware_is_connected

    def get_attributes(self):
        return {
            'hardware_is_connected': self.hardware_is_connected
        }
