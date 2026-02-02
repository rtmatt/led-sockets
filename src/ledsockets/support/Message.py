import json
from typing import Dict


class MessageException(Exception):
    pass


class Message:
    def __init__(self, type: str, payload: Dict):
        self.type = type
        self.payload = payload

    def toJson(self):
        return json.dumps([
            self.type,
            self.payload
        ])

    @classmethod
    def parse(cls, message: str):
        try:
            data = json.loads(message)
            message_type = data[0]
            message_payload = data[1]
            if not message_type:
                raise MessageException("No message type provided")
        except json.JSONDecodeError as e:
            raise MessageException('Non-JSON payload') from e
        except KeyError as e:
            message = str(e)
            message = 'no message type provided' if message == '0' else "no message payload provided"
            raise MessageException(f"Payload key error: {message}") from e

        return cls(message_type, message_payload)
