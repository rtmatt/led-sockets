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
    def from_attributes(self, attributes):
        if not isinstance(attributes, Dict):
            raise DTOInvalidAttributesException('Attributes are not an object')
        inst = PartialHardwareState()
        try:
            inst.on = attributes.get('on')
            inst.message = attributes.get('message')
        except KeyError as e:
            raise DTOInvalidAttributesException('Invalid Partial Hardware State attributes') from e
        return inst

    @classmethod
    def from_message(self, message: Message):
        try:
            if (message.type != 'patch_hardware_state'):
                raise DTOInvalidAttributesException('Invalid source message')
            attributes = message.payload['data']['attributes']
            return self.from_attributes(attributes)
        except KeyError as e:
            raise DTOInvalidAttributesException('Invalid Partial Hardware State attributes') from e
