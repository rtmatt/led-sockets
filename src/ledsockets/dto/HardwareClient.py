from ledsockets.dto.AbstractDto import AbstractDto


class HardwareClient(AbstractDto):
    TYPE = 'hardware_client'

    def __init__(self, id, connection):
        super().__init__(id)
        self.connection = connection

    def get_attributes(self):
        return {}
