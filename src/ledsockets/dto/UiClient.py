from ledsockets.dto.AbstractDto import AbstractDto


class UiClient(AbstractDto):
    TYPE = 'ui_client'

    def __init__(self, id: str, connection):
        super().__init__(id)
        self.connection = connection

    @property
    def name(self):
        return f"Client {self.id}"

    def get_attributes(self):
        return {
            "name": self.name
        }
