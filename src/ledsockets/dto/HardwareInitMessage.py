from ledsockets.dto.AbstractDto import AbstractDto
from ledsockets.dto.HardwareState import HardwareState


class HardwareInitMessage(AbstractDto):
    TYPE = 'init_hardware'

    def __init__(self, hardware_state: HardwareState, id=''):
        super().__init__(id)
        self.hardware_state = hardware_state

    def get_attributes(self):
        pass

    def get_relationships(self):
        return {
            "hardware_state": {
                "data": self.hardware_state.toDict()
            }
        }
