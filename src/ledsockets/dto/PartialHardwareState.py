from typing import Dict

from ledsockets.dto.HardwareState import HardwareState


class PartialHardwareState(HardwareState):
    TYPE = 'hardware_state_partial'

    def __init__(self, on=None, status_description=None, id=''):
        super().__init__(id=id)
        self.on = on
        self.status_description = status_description

    def get_attributes(self):
        result = {}
        if (self.on is not None):
            result['on'] = self.on
        if (self.status_description is not None):
            result['status_description'] = self.status_description
        return result

    @classmethod
    def _inst_from_attributes(cls, attributes: Dict, id: str = ''):
        return PartialHardwareState(attributes.get('on'), attributes.get('status_description'), id)
