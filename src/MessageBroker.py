from abc import ABC, abstractmethod


class MessageBroker(ABC):

    @abstractmethod
    async def send_message(self, message):
        pass
