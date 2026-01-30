from ledsockets.dto.AbstractDto import AbstractDto


class ConnectedHardware(AbstractDto):
    TYPE = 'connected_hardware'
    def __init__(self, id, connection):
        super().__init__(id)
        self.connection = connection

    def get_attributes(self):
        return {}

    def getConnection(self):
        return self.connection
