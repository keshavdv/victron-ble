import abc


class Device(abc.ABC):
    def __init__(self, advertisement_key: str):
        self.advertisement_key = advertisement_key

    @abc.abstractmethod
    def parse(self, data: bytes):
        pass
