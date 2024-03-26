from typing import Optional

from victron_ble.devices.base import (
    AlarmReason,
    BitReader,
    Device,
    DeviceData,
    OperationMode,
)


class InverterData(DeviceData):
    def get_device_state(self) -> OperationMode:
        """
        Return an enum indicating the current device state
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

    def get_ac_apparent_power(self) -> int:
        """
        Return the output AC power in voltampere
        """
        return self._data["ac_apparent_power"]

    def get_ac_voltage(self) -> float:
        """
        Return the output AC voltage in volts
        """
        return self._data["ac_voltage"]

    def get_ac_current(self) -> float:
        """
        Return the output AC current in amperes
        """
        return self._data["ac_current"]


class Inverter(Device):
    data_type = InverterData

    def parse_decrypted(self, decrypted: bytes) -> dict:
        reader = BitReader(decrypted)

        # Device State:   0 - Off
        device_state = reader.read_unsigned_int(8)
        # Alarm Reason Code
        alarm = reader.read_unsigned_int(16)
        # Input voltage reading in 0.01V increments
        battery_voltage = reader.read_signed_int(16)
        # Output AC power in 1VA
        ac_apparent_power = reader.read_unsigned_int(16)
        # Output AC voltage in 0.01V
        ac_voltage = reader.read_unsigned_int(15)
        # Output AC current in 0.1A
        ac_current = reader.read_unsigned_int(11)

        return {
            "device_state": (
                OperationMode(device_state) if device_state != 0xFF else None
            ),
            "alarm": alarm,
            "battery_voltage": (
                (battery_voltage) / 100 if battery_voltage != 0x7FFF else None
            ),
            "ac_apparent_power": (
                ac_apparent_power if ac_apparent_power != 0xFFFF else None
            ),
            "ac_voltage": ac_voltage / 100 if ac_voltage != 0x7FFF else None,
            "ac_current": ac_current / 10 if ac_current != 0x7FF else None,
        }
