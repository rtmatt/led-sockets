import json
from abc import ABC, abstractmethod


class DTOInvalidAttributesException(Exception):
    pass

class DTOInvalidPayloadException(Exception):
    pass

class AbstractDto(ABC):
    TYPE = ''

    def __init__(self, id=''):
        self.id = id

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
        return None
