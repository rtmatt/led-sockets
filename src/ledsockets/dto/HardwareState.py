from typing import Dict

from ledsockets.dto.AbstractDto import AbstractDto
from ledsockets.dto.ChangeDetail import ChangeDetail
from ledsockets.dto.UiClient import UiClient


class HardwareState(AbstractDto):
    TYPE = 'hardware_state'

    def __init__(self, on=False, status_description='', id=''):
        super().__init__(id)
        self.on = on
        self.status_description = status_description
        self._source = None
        self._change_detail = None

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

    @property
    def change_detail(self):
        return self._change_detail

    @change_detail.setter
    def change_detail(self, val: ChangeDetail | None):
        if (not isinstance(val, ChangeDetail)):
            raise TypeError("Invalid change_detail")
        self._change_detail = val
        if (val):
            self.set_relationship('change_detail', val)
        else:
            self.remove_relationship('change_detail')

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

            change_relation = relationships.get('change_detail')
            change_relation_data = change_relation.get('data') if change_relation else None
            if (change_relation_data):
                if (change_relation_data.get('type') == 'change_detail'):
                    detail = ChangeDetail.from_dict(change_relation_data)
                    instance.change_detail = detail

        return instance

    @classmethod
    def _inst_from_attributes(cls, attributes: Dict, id: str = ''):
        return cls(attributes['on'], attributes['status_description'], id)
