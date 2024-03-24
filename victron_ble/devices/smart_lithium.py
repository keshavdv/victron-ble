from typing import Optional

from construct import Array, BitsInteger, BitStruct, ByteSwapped, Padding

from victron_ble.devices.base import Device, DeviceData

from enum import Enum

class BalancerStatus(Enum):
  UNKNOWN = 0
  BALANCED = 1
  BALANCING = 2 //?
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

    # https://community.victronenergy.com/questions/187303/victron-bluetooth-advertising-protocol.html
    # Reverse the entire packet, because non-aligned integers are packed
    # little-endian
    PACKET = ByteSwapped(
        BitStruct(
            Padding(1),  # unused
            "battery_temperature" / BitsInteger(7),  # -40..86C
            "balancer_status" / BitsInteger(4),  # 0 = unknown, 1 = balanced, 3 = imbalance
            "battery_voltage" / BitsInteger(12),  # (0V.. +0.01V .. 40.95V)
            # Cell voltage reading 7 bit * 8 cells (0x00<2.61V, 0x01=2.61V, +0.01V .. 0x7e>3.85V, 0x7f N/A)
            "cell_voltages" / Array(8, BitsInteger(7)),
            "error_flags" / BitsInteger(16),
            "bms_flags" / BitsInteger(32, swapped=True),
        ),
    )

    def parse_decrypted(self, decrypted: bytes) -> dict:
        pkt = self.PACKET.parse(decrypted[:20])

        parsed = {
            "bms_flags": pkt.bms_flags,
            "error_flags": pkt.error_flags,
            "cell_voltages": [
                parse_cell_voltage(v) for v in reversed(pkt.cell_voltages)
            ],
            "battery_voltage": (
                pkt.battery_voltage / 100.0 if pkt.battery_voltage != 0x0FFF else None
            ),
            "balancer_status": BalancerStatus(pkt.balancer_status),
            "battery_temperature": (
                (pkt.battery_temperature - 40)
                if pkt.battery_temperature != 0x7F
                else None
            ),  # Celsius
        }

        return parsed


def parse_cell_voltage(payload: int) -> Optional[float]:
    return {0x00: float("-inf"), 0x7E: float("inf"), 0x7F: None}.get(
        payload, (260 + payload) / 100.0
    )
