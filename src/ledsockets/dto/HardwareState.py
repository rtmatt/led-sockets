from typing import Dict

from ledsockets.dto.AbstractDto import AbstractDto


class HardwareState(AbstractDto):
    TYPE = 'hardware_state'

    def __init__(self, on=False, message='', id=''):
        super().__init__(id)
        self.on = on
        self.message = message

    def get_attributes(self):
        return {
            "on": self.on,
            "message": self.message
        }

    def copy(self):
        return HardwareState(self.on, self.message)

    @classmethod
    def _inst_from_attributes(cls, attributes: Dict, id: str = ''):
        return cls(on=attributes['on'], message=attributes['message'], id=id)
