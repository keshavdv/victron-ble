import abc

from construct import FixedSized, GreedyBytes, Int8sl, Int16ul, Struct
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad


class Device(abc.ABC):
    def __init__(self, advertisement_key: str):
        self.advertisement_key = advertisement_key

    def decrypt(self, data: bytes):
        parser = Struct(
            "prefix" / FixedSized(2, GreedyBytes),
            # Model ID
            "device_id" / Int16ul,
            # Packet type
            "readout_type" / Int8sl,
            # IV for encryption
            "iv" / Int16ul,
            "encrypted_data" / GreedyBytes,
        )

        container = parser.parse(data)

        # The first byte of advertised data seems to match the first byte of the advertisement key
        cipher = AES.new(
            bytes.fromhex(self.advertisement_key),
            AES.MODE_OFB,
            iv=container.iv.to_bytes(16, "little"),
        )
        return cipher.decrypt(pad(container.encrypted_data[1:], 16))

    @abc.abstractmethod
    def parse(self, data: bytes):
        pass
