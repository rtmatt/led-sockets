from typing import Dict

from ledsockets.dto.AbstractDto import AbstractDto
from ledsockets.dto.ConnectedClient import ConnectedClient


class DtoParseException(Exception):
    pass


class PatchHardwareState(AbstractDto):
    TYPE = "patch_hardware_state"

    def __init__(self, on: bool | None = None, message: str | None = None, id=''):
        super().__init__(id)
        self.on: bool | None = on
        self.message: str | None = message
        self.client: ConnectedClient | None = None

    def get_attributes(self):
        result = {}
        if self.on is not None:
            result['on'] = self.on
        if self.message is not None:
            result['message'] = self.message
        return result

    def get_relationships(self):
        result = {}
        if self.client:
            result['client'] = {
                "data": self.client.toDict()
            }
        return result

    def setClient(self, client: ConnectedClient):
        self.client = client

    @classmethod
    def fromPayload(cls, payload: Dict):
        try:
            type = payload['type']
            attributes = payload['attributes']
        except KeyError as e:
            raise DtoParseException(f"Key error: {e}") from e

        if type != cls.TYPE:
            raise DtoParseException(f"Invalid type data: {type}")

        return cls.fromAttributes(attributes)

    @classmethod
    def fromAttributes(cls, attributes: Dict):
        result = cls(
            on=attributes.get('on'),
            message=attributes.get('message')
        )

        return result
