from typing import Dict

from ledsockets.dto.AbstractDto import AbstractDto
from ledsockets.dto.ChangeDetail import ChangeDetail
from ledsockets.dto.UiClient import UiClient


class ServerStatus(AbstractDto):
    TYPE = 'server_status'

    def __init__(self, hardware_is_connected: bool, id=''):
        super().__init__(id)
        self.hardware_is_connected = hardware_is_connected
        self._ui_client = None
        self._change_detail = None

    @property
    def ui_client(self):
        return self._ui_client

    @ui_client.setter
    def ui_client(self, val: UiClient):
        self._ui_client = val
        if (val):
            self.set_relationship('ui_client', val)
        else:
            self.remove_relationship('ui_client')

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
            'hardware_is_connected': self.hardware_is_connected
        }

    @classmethod
    def from_dict(self, json_data: Dict):
        instance = super().from_dict(json_data)
        relationships = json_data.get('relationships')
        if (relationships):
            change_relation = relationships.get('change_detail')
            change_relation_data = change_relation.get('data') if change_relation else None
            if (change_relation_data):
                if (change_relation_data.get('type') == 'change_detail'):
                    detail = ChangeDetail.from_dict(change_relation_data)
                    instance.change_detail = detail

        return instance

    @classmethod
    def _inst_from_attributes(cls, attributes: Dict, id: str = ''):
        return cls(bool(attributes.get('hardware_is_connected')))
