from ledsockets.dto.AbstractDto import AbstractDto
from ledsockets.dto.HardwareState import HardwareState
from ledsockets.dto.UiMessage import UiMessage


class ClientConnectionInitMessage(AbstractDto):
    TYPE = 'client_init'

    def __init__(self, hardware_is_connected, message, hardware_state: HardwareState, id=''):
        super().__init__(id)
        self.hardware_is_connected = hardware_is_connected
        self.message = message
        self.hardware_state = hardware_state
        self.ui_message = UiMessage('You are connected')

    def get_attributes(self):
        return {
            "hardware_is_connected": self.hardware_is_connected,
            "message": self.message
        }

    def get_relationships(self):
        return {
            "hardware_state": {
                "data": self.hardware_state.toDict()
            },
            "ui_message": {
                "data": self.ui_message.toDict()
            }
        }
