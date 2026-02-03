import json
from abc import ABC, abstractmethod
from typing import Dict, List


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
