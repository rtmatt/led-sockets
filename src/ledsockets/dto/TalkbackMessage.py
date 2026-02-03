from typing import Dict

from ledsockets.dto.AbstractDto import AbstractDto


class TalkbackMessage(AbstractDto):
    TYPE = 'talkback_message'

    def __init__(self, message, id=""):
        AbstractDto.__init__(self, id)
        self.message = message

    def get_attributes(self):
        return {
            "message": self.message
        }

    @classmethod
    def _inst_from_attributes(cls, attributes: Dict, id: str = ''):
        return cls(attributes['message'], id)
