from ledsockets.dto.AbstractDto import AbstractDto


class HardwareConnectionMessage(AbstractDto):
    TYPE = "hardware_connection"

    def __init__(self, is_connected, hardware_state, id=''):
        super().__init__(id)
        self.is_connected = is_connected
        self.hardware_state = hardware_state

    def get_attributes(self):
        return {
            "is_connected": self.is_connected
        }

    def get_relationships(self):
        return {
            "hardware_state": {
                "data": self.hardware_state.toDict()
            }
        }
