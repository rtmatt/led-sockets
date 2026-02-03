from typing import Dict

from ledsockets.dto.HardwareState import HardwareState


class PartialHardwareState(HardwareState):
    TYPE = 'hardware_state_partial'

    def __init__(self, on=None, message=None, id=''):
        super().__init__(id=id)
        self.on = on
        self.message = message

    def get_attributes(self):
        result = {}
        if (self.on is not None):
            result['on'] = self.on
        if (self.message is not None):
            result['message'] = self.message
        return result

    @classmethod
    def _inst_from_attributes(cls, attributes: Dict, id: str = ''):
        return PartialHardwareState(on=attributes.get('on'), message=attributes.get('message'), id=id)
