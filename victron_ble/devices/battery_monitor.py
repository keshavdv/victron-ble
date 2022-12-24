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


class BatteryMonitor(Device):

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
        # Remaining time in minutes
        "remaining_mins" / Int16ul,
        # Voltage reading in 0.1v increments
        "voltage" / Int16ul,
        # Bit map of alarm status
        # 0b00000001 = low voltage alarm
        # 0b00000010 = high voltage alarm
        # 0b00000100 = low soc alarm
        # 0b00001000 = low starter alarm
        # 0b00001001 = low voltage + low starter alarm
        # 0b00011001 = high starter + low voltage + low starter alarm
        # 0b00010000 = high starter alarm
        # 0b00100000 = low temp alarm
        # 0b01000000 = high temp alarm
        # 0b10000000 = midpoint voltage deviation alarm
        "alarm"
        / BitStruct(
            "mid_voltage" / Flag,
            "high_temperature" / Flag,
            "low_temperature" / Flag,
            "high_starter_voltage" / Flag,
            "low_starter_voltage" / Flag,
            "low_soc" / Flag,
            "high_voltage" / Flag,
            "low_voltage" / Flag,
        ),
        # Unknown byte
        "uk_1b" / Int8sl,
        # Value of the auxillary input (millivolts or degrees)
        "aux" / Int16sl,
        # The upper 22 bits indicate the current in milliamps
        # The lower 2 bits identify the aux input mode:
        #   0 = Starter battery voltage
        #   1 = Midpoint voltage
        #   2 = Temperature
        #   3 = Disabled
        "current" / Int24sl,
        # Consumed Ah in 0.1Ah increments
        "consumed_ah" / Int16ul,
        # The lowest 4 bits are unknown
        # The next 8 bits indicate the state of charge in 0.1% increments
        # The upper 2 bits are unknown
        "soc" / Int16ul,
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
            "remaining_mins": pkt.remaining_mins,
            "aux_mode": pkt.current & 0b11,
            "aux": pkt.aux,
            "current": pkt.current >> 2,
            "voltage": pkt.voltage / 100,
            "consumed_ah": pkt.consumed_ah / 10,
            "soc": ((pkt.soc & 0x3FFF) >> 4) / 10,
            "alarm": {
                "low_voltage": pkt.alarm.low_voltage,
                "high_voltage": pkt.alarm.high_voltage,
                "low_soc": pkt.alarm.low_soc,
                "low_starter_voltage": pkt.alarm.low_starter_voltage,
                "high_starter_voltage": pkt.alarm.high_starter_voltage,
                "low_temperature": pkt.alarm.low_temperature,
                "high_temperature": pkt.alarm.high_temperature,
                "mid_voltage": pkt.alarm.mid_voltage,
            },
        }
