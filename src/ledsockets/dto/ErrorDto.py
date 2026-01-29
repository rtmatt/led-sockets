from ledsockets.dto.AbstractDto import AbstractDto


class ErrorDto(AbstractDto):
    TYPE = 'error'

    def __init__(self, message, id=""):
        AbstractDto.__init__(self, id)
        self.message = message

    def get_attributes(self):
        return {
            "message": self.message
        }
