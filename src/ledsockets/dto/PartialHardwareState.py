from typing import Dict

from ledsockets.dto.AbstractDto import AbstractDto, DTOInvalidAttributesException
from ledsockets.support.Message import Message


class PartialHardwareState(AbstractDto):
    TYPE = 'hardware_state'

    def __init__(self, on=None, message=None, id=''):
        super().__init__(id)
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
