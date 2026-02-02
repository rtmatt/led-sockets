from ledsockets.dto.AbstractDto import AbstractDto


class UiMessage(AbstractDto):
    TYPE = 'ui_message'

    def __init__(self, message, id=''):
        super().__init__(id)
        self.message = message

    def get_attributes(self):
        return {
            "message": self.message
        }
