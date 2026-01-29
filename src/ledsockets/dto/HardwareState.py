from ledsockets.dto.AbstractDto import AbstractDto, DTOInvalidAttributesException


class HardwareState(AbstractDto):
    TYPE = 'hardware_state'

    def __init__(self, on=False, message='', id=''):
        super().__init__(id)
        self.on = on
        self.message = message

    def get_attributes(self):
        return {
            "on": self.on,
            "message": self.message
        }

    def copy(self):
        return HardwareState(self.on, self.message)

    @classmethod
    def from_attributes(self, attributes):
        inst = HardwareState()
        try:
            inst.on = attributes['on']
            inst.message = attributes['message']
        except KeyError as e:
            raise DTOInvalidAttributesException('Invalid Hardware State attributes') from e
        return inst
