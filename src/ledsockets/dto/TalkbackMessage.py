from ledsockets.dto.AbstractDto import AbstractDto, DTOInvalidPayloadException
from ledsockets.support.Message import Message


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
    def from_message(cls, message: Message):
        try:
            data = message.payload['data']
            attributes = data['attributes']
            return cls(attributes['message'])
        except KeyError as e:
            raise DTOInvalidPayloadException(f'Payload missing key {e}') from e
