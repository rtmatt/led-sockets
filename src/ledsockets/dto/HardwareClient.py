from typing import Dict

from ledsockets.dto.AbstractDto import AbstractDto


class HardwareClient(AbstractDto):
    TYPE = 'hardware_client'

    def __init__(self, id, connection):
        super().__init__(id)
        self.connection = connection

    def get_attributes(self):
        return {}

    @classmethod
    def _inst_from_attributes(cls, attributes: Dict, id: str = ''):
        return cls(id, None)
