from construct import (
    BitStruct,
    FixedSized,
    Flag,
    GreedyBytes,
    Int8sl,
    Int16sl,
    Int16ul,
    Int24sl,
    Struct,
)
from Crypto.Cipher import AES

from victron_ble.devices.base import Device


class SmartBatterySense(Device):

    CONTAINER = Struct(
        "prefix" / FixedSized(2, GreedyBytes),
        # Model ID
        "device_id" / Int16ul,
        # Battery monitor vs DC Energy Meter
        "battery_monitor_mode" / Int8sl,
        # IV for encryption
        "iv" / Int16ul,
        "encrypted_data" / FixedSized(16, GreedyBytes),
    )

    PACKET = Struct(
        # Unknown bytes
        "uk1_2b" / Int16ul,
        # Voltage reading in 0.1v increments
        "voltage" / Int16ul,
        # Unknown bytes
        "uk2_2b" / Int16ul,
        # Temperaturee in Kelvin
        "temperature" / Int16ul,
        # Throw away any extra bytes
        GreedyBytes,
    )

    def parse(self, data: bytes):
        container = self.CONTAINER.parse(data)

        # The first byte of advertised data seems to match the first byte of the advertisement key
        cipher = AES.new(
            bytes.fromhex(self.advertisement_key),
            AES.MODE_OFB,
            iv=container.iv.to_bytes(16, "little"),
        )
        decrypted = cipher.decrypt(container.encrypted_data[1:] + b"\x0f")

        pkt = self.PACKET.parse(decrypted)

        return {
            "voltage": pkt.voltage / 100,
            "temperatureK": pkt.temperature / 100,
            "temperatureC": round((pkt.temperature / 100) - 273.15, 2),
            "temperatureF": round(((pkt.temperature / 100) * (9/5)) - 459.67, 2),
        }
