from ledsockets.dto.AbstractDto import AbstractDto


class TalkbackMessage(AbstractDto):
    def __init__(self, message, id=""):
        self.message = message
        self.id = id

    def get_json_data(self):
        return {
            "type": 'talkback_message',
            "id": self.id,
            "attributes": {
                "message": self.message
            }
        }
