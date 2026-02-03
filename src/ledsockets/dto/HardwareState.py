from typing import Dict

from ledsockets.dto.AbstractDto import AbstractDto


class HardwareState(AbstractDto):
    TYPE = 'hardware_state'

    def __init__(self, on=False, status_description='', id=''):
        super().__init__(id)
        self.on = on
        self.status_description = status_description

    def get_attributes(self):
        return {
            "on": self.on,
            "status_description": self.status_description
        }

    def copy(self):
        return HardwareState(self.on, self.status_description)

    @classmethod
    def _inst_from_attributes(cls, attributes: Dict, id: str = ''):
        return cls(attributes['on'], attributes['status_description'], id)
