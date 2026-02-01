from ledsockets.dto.AbstractDto import AbstractDto


class ConnectedClient(AbstractDto):
    TYPE = 'connected_client'

    def __init__(self, id, connection):
        super().__init__(id)
        self.connection = connection

    @property
    def name(self):
        return f"Client {self.id}"

    def get_attributes(self):
        return {
            "name": self.name
        }

    def getConnection(self):
        return self.connection
