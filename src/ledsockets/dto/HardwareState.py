from typing import Dict

from ledsockets.dto.AbstractDto import AbstractDto
from ledsockets.dto.UiClient import UiClient


class HardwareState(AbstractDto):
    TYPE = 'hardware_state'

    def __init__(self, on=False, status_description='', id=''):
        super().__init__(id)
        self.on = on
        self.status_description = status_description
        self._source = None

    @property
    def source(self):
        return self._source

    @source.setter
    def source(self, val: UiClient | None):
        self._source = val
        if (val):
            self.set_relationship('source', val)
        else:
            self.remove_relationship('source')

    def get_attributes(self):
        return {
            "on": self.on,
            "status_description": self.status_description
        }

    def copy(self):
        return HardwareState(self.on, self.status_description)

    @classmethod
    def from_dict(self, json_data: Dict):
        instance = super().from_dict(json_data)
        relationships = json_data.get('relationships')
        if (relationships):
            source_relationship = relationships.get('source')
            source_relation_data = source_relationship.get('data') if source_relationship else None
            if (source_relation_data):
                if (source_relation_data.get('type') == 'ui_client'):
                    client = UiClient.from_dict(source_relation_data)
                    instance.source = client

        return instance

    @classmethod
    def _inst_from_attributes(cls, attributes: Dict, id: str = ''):
        return cls(attributes['on'], attributes['status_description'], id)
