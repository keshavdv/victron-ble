from construct import GreedyBytes, Int8ul, Int16sl, Int16ul, Struct
from typing import Optional, Type

from victron_ble.devices.base import (
    AlarmReason,
    Device,
    DeviceData,
    OperationMode,
)


class InverterData(DeviceData):
    def get_charge_state(self) -> OperationMode:
        """
        Return an enum indicating the current charging state
        """
        return self._data["device_state"]

    def get_alarm(self) -> Optional[AlarmReason]:
        """
        Return an enum indicating the current alarm reason or None otherwise
        """
        return AlarmReason(self._data["alarm"]) if self._data["alarm"] > 0 else None

    def get_battery_voltage(self) -> float:
        """
        Return the battery voltage in volts
        """
        return self._data["battery_voltage"]

    def get_AC_apparent_power(self) -> int:
        """
        Return the output AC power in voltampere
        """
        return self._data["AC_apparent_power"]

    def get_AC_voltage(self) -> float:
        """
        Return the output AC voltage in volts
        """
        return self._data["AC_voltage"]

    def get_AC_current(self) -> float:
        """
        Return the output AC current in amperes
        """
        return self._data["AC_current"]

class Inverter(Device):
    data_type = InverterData

    PACKET = Struct(
        # Device State:   0 - Off
        "device_state" / Int8ul,
        # Alarm Reason Code
        "alarm" / Int16ul,
        # Input voltage reading in 0.01V increments
        "battery_voltage" / Int16sl,
        # Output AC power in 1VA
        "AC_apparent_power" / Int16ul,

        # Output AC voltage in 0.01V
        # The next 15 bits indicate the voltage in 0.01 V (0 .. 327.66 V | 0x7FFF)
        "AC_voltage"/ Int16ul,

        # Output AC current in 0.1A
        # The next 11 bits identify the current in 0.1 A (0 .. 204.6 A | 0x7FF)
        # enconding in little endian (Int16ul)
        "AC_current"/ Int16ul,
        GreedyBytes,
    )

    def parse_decrypted(self, decrypted: bytes) -> dict:
        pkt = self.PACKET.parse(decrypted)

        return {
            "device_state": OperationMode(pkt.device_state),
            "alarm": pkt.alarm,
            "battery_voltage": (pkt.battery_voltage) / 100,
            "AC_apparent_power": pkt.AC_apparent_power,
            "AC_voltage": (pkt.AC_voltage & 0x7FFF) / 100,
            "AC_current": ((pkt.AC_voltage >> 15 | pkt.AC_current << 1) & 0x7FF) / 10,
        }
