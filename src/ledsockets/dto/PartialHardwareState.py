from typing import Dict

from ledsockets.dto.AbstractDto import AbstractDto
from ledsockets.dto.UiClient import UiClient


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
    def from_dict(self, json_data: Dict):
        instance = super().from_dict(json_data)
        relationships = json_data.get('relationships')
        if (relationships):
            source_relation_data = relationships.get('source').get('data')
            if (source_relation_data):
                if (source_relation_data.get('type') == 'ui_client'):
                    client = UiClient.from_dict(source_relation_data)
                    instance.set_relationship('source', client)

        return instance

    @classmethod
    def _inst_from_attributes(cls, attributes: Dict, id: str = ''):
        return PartialHardwareState(on=attributes.get('on'), message=attributes.get('message'), id=id)
