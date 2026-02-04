from typing import Dict

from ledsockets.dto.AbstractDto import AbstractDto


class UiClient(AbstractDto):
    TYPE = 'ui_client'

    def __init__(self, id: str, connection, name=None):
        super().__init__(id)
        self.connection = connection
        self.name: str | None = name

    def get_attributes(self):
        return {
            "name": self.name
        }

    @classmethod
    def _inst_from_attributes(cls, attributes: Dict, id: str = ''):
        inst = cls(id, None, attributes.get('name'))
        return inst
