from enum import Enum
from typing import Optional

from victron_ble.devices.base import BitReader, Device, DeviceData


class BalancerStatus(Enum):
    UNKNOWN = 0
    BALANCED = 1
    BALANCING = 2
    IMBALANCE = 3


class SmartLithiumData(DeviceData):
    def get_bms_flags(self) -> int:
        """
        Get the raw bms_flags field (meaning not documented).
        """
        return self._data["bms_flags"]

    def get_error_flags(self) -> int:
        """
        Get the raw error_flags field (meaning not documented).
        """
        return self._data["error_flags"]

    def get_battery_voltage(self) -> Optional[float]:
        """
        Return the voltage in volts
        """
        return self._data["battery_voltage"]

    def get_battery_temperature(self) -> int:
        """
        Return the temperature in Celsius if the aux input is set to temperature
        """
        return self._data["battery_temperature"]

    def get_cell_voltages(self) -> list:
        """
        Return the voltage of each cell (floats where -inf is <2.61V, +inf is >3.85V, None is N/A)
        """
        return self._data["cell_voltages"]

    def get_balancer_status(self) -> BalancerStatus:
        """
        Get the raw balancer_status field (meaning not documented).
        """
        return self._data["balancer_status"]


class SmartLithium(Device):
    data_type = SmartLithiumData

    def parse_decrypted(self, decrypted: bytes) -> dict:
        reader = BitReader(decrypted)
        bms_flags = reader.read_unsigned_int(32)
        error_flags = reader.read_unsigned_int(16)
        cell_voltages = [reader.read_unsigned_int(7) for _ in range(8)]
        battery_voltage = reader.read_unsigned_int(12)
        balancer_status = reader.read_unsigned_int(4)
        battery_temperature = reader.read_unsigned_int(7)

        parsed = {
            "bms_flags": bms_flags,
            "error_flags": error_flags,
            "cell_voltages": [parse_cell_voltage(v) for v in cell_voltages],
            "battery_voltage": (
                battery_voltage / 100.0 if battery_voltage != 0x0FFF else None
            ),
            "balancer_status": (
                BalancerStatus(balancer_status) if balancer_status != 0xF else None
            ),
            "battery_temperature": (
                (battery_temperature - 40) if battery_temperature != 0x7F else None
            ),  # Celsius
        }

        return parsed


def parse_cell_voltage(payload: int) -> Optional[float]:
    return {0x00: float("-inf"), 0x7E: float("inf"), 0x7F: None}.get(
        payload, (260 + payload) / 100.0
    )
