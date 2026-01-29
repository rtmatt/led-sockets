import json
from abc import ABC, abstractmethod


class AbstractDto(ABC):
    def toJSON(self):
        return json.dumps(self.get_json_data())

    @abstractmethod
    def get_json_data(self):
        pass
