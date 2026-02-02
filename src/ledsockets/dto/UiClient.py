from typing import Dict

from ledsockets.dto.AbstractDto import AbstractDto


class UiClient(AbstractDto):
    TYPE = 'ui_client'

    def __init__(self, id: str, connection):
        super().__init__(id)
        self.connection = connection
        self.name = f"Client {self.id}"

    def get_attributes(self):
        return {
            "name": self.name
        }

    @classmethod
    def _inst_from_attributes(cls, attributes: Dict, id: str = ''):
        inst = cls(id, None)
        inst.name = attributes['name']
        return inst
