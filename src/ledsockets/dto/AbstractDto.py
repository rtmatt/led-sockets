import json
from abc import ABC, abstractmethod
from typing import Dict, List

from ledsockets.support.Message import Message


class DTOInvalidAttributesException(Exception):
    pass


class DTOInvalidPayloadException(Exception):
    pass


class AbstractDto(ABC):
    TYPE = ''

    def __init__(self, id=''):
        self.id = id
        self.relationships = None

    @property
    def type(self):
        return self.TYPE

    def toJSON(self):
        result = self.toDict()

        return json.dumps(result)

    def toDict(self):
        result = {
            "type": self.TYPE,
            "id": self.id,
            "attributes": self.get_attributes()
        }
        relationships = self.get_relationships()
        if relationships:
            result['relationships'] = relationships
        return result

    @abstractmethod
    def get_attributes(self):
        pass

    def get_relationships(self):
        return self.relationships

    def set_relationship(self, key, model):
        """
        :param key: str
        :param model: AbstractDto | Dict
        """
        if self.relationships is None:
            self.relationships = {}
        data = model
        if isinstance(model, AbstractDto):
            data = model.toDict()
        if not isinstance(data, Dict):
            raise DTOInvalidPayloadException('Invalid relationship data')
        self.relationships[key] = {
            "data": data
        }

    def append_relationship(self, key, model):
        """
        :param key: str
        :param model: AbstractDto | Dict
        """
        if self.relationships is None:
            self.relationships = {}
        data = model
        if isinstance(model, AbstractDto):
            data = model.toDict()
        if not isinstance(data, Dict):
            raise DTOInvalidPayloadException('Invalid relationship data')
        if (not self.relationships.get(key)):
            self.relationships[key] = {
                "data": []
            }
        data_list = self.relationships[key].get('data')
        if (isinstance(data_list, Dict)):
            data_list = [data_list]
        if (not isinstance(data_list, List)):
            raise DTOInvalidPayloadException('Is not a list')

        data_list.append(data)

    def remove_relationship(self, key: str):
        if (self.relationships):
            if key in self.relationships.keys():
                del self.relationships[key]

    @classmethod
    def from_attributes(self, attributes: Dict, id: str = ''):
        if not isinstance(attributes, Dict):
            raise DTOInvalidPayloadException('Attributes are not an object')
        try:
            return self._inst_from_attributes(attributes, id)
        except KeyError as e:
            raise DTOInvalidAttributesException(f'Invalid {self.TYPE} attributes') from e

    @classmethod
    def from_dict(self, json_data: Dict):
        if not isinstance(json_data, Dict):
            raise DTOInvalidAttributesException('Dictionary is not an object')

        type = json_data.get('type')
        attributes = json_data.get('attributes')
        id = json_data.get('id')

        if type != self.TYPE:
            raise DTOInvalidPayloadException('Data type mismatch')
        if attributes is None:
            raise DTOInvalidPayloadException('No attributes')

        inst = self.from_attributes(attributes, id)
        return inst

    @classmethod
    @abstractmethod
    def _inst_from_attributes(cls, attributes: Dict, id: str = ''):
        raise Exception(f'"_inst_from_attributes" not defined for {cls.TYPE}')

    @classmethod
    def from_message(self, message: Message):
        try:
            payload_data = message.payload['data']
            type_ = payload_data['type']
            if (type_ != self.TYPE):
                raise DTOInvalidPayloadException(f'Invalid source type "{type_}"')

            instance = self.from_dict(payload_data)
            return instance
        except KeyError as e:
            raise DTOInvalidPayloadException(f'Invalid {self.TYPE} payload/attributes') from e
