from ledsockets.dto.AbstractDto import AbstractDto
from ledsockets.dto.UiMessage import UiMessage


class HardwareConnectionMessage(AbstractDto):
    TYPE = "hardware_connection"

    def __init__(self, is_connected, hardware_state, id=''):
        super().__init__(id)
        self.is_connected = is_connected
        self.hardware_state = hardware_state
        message = "Hardware connected" if is_connected else "Hardware disconnected"
        self._ui_message: UiMessage = UiMessage(message)

    def get_attributes(self):
        return {
            "is_connected": self.is_connected
        }

    def get_relationships(self):
        return {
            "hardware_state": {
                "data": self.hardware_state.toDict()
            },
            "ui_message": {
                "data": self._ui_message.toDict()
            }
        }
