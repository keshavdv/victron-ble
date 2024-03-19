from enum import Enum
from construct import Byte, Struct, Int8ul, Int16ul, Int32ul
from victron_ble.devices.base import Device, DeviceData


def _convert_cell_voltage(cell_voltage: int | None) -> float:
    # 0x7F is a special value that indicates the cell voltage is not available - return None
    # 0x7E means the cell voltage is too high to measure (>=3.86) - return 3.86
    # 0x00 means the cell voltage is too low to measure (<=2.60) - return 2.60
    if cell_voltage == 0x7F:
        return None
    return round(cell_voltage / 100.0 + 2.60, 2)


class BalancerStatus(Enum):
    """TODO: not documented by Victron, 4 bits"""

    BALANCED = 1  # confirmed from testing
    UNBALANCED = 2  # this is an educated guess
    UNKNOWN = 3  # this is an educated guess


class SmartLithiumData(DeviceData):
    def get_cell1_voltage(self) -> float:
        """
        Return the voltage of cell 1 in volts
        """
        return self._data["cell1_voltage"]

    def get_cell2_voltage(self) -> float:
        """
        Return the voltage of cell 2 in volts
        """
        return self._data["cell2_voltage"]

    def get_cell3_voltage(self) -> float:
        """
        Return the voltage of cell 3 in volts
        """
        return self._data["cell3_voltage"]

    def get_cell4_voltage(self) -> float:
        """
        Return the voltage of cell 4 in volts
        """
        return self._data["cell4_voltage"]

    def get_cell5_voltage(self) -> float:
        """
        Return the voltage of cell 5 in volts
        """
        return self._data["cell5_voltage"]

    def get_cell6_voltage(self) -> float:
        """
        Return the voltage of cell 6 in volts
        """
        return self._data["cell6_voltage"]

    def get_cell7_voltage(self) -> float:
        """
        Return the voltage of cell 7 in volts
        """
        return self._data["cell7_voltage"]

    def get_cell8_voltage(self) -> float:
        """
        Return the voltage of cell 8 in volts
        """
        return self._data["cell8_voltage"]

    def get_battery_voltage(self) -> float:
        """
        Return the battery voltage in volts
        """
        return self._data["battery_voltage"]

    def get_battery_temperature(self) -> float:
        """
        Return the battery temperature in degrees celsius
        """
        return self._data["battery_temperature"]

    def get_bms_flags(self) -> str:
        """
        Return the BMS flags
        TODO: return useful flags rather than just the raw bitmask
        """
        return bin(self._data["bms_flags"])

    def get_smart_lithium_error(self) -> str:
        """
        Return the Smart Lithium error flags
        TODO: return useful flags rather than just the raw bitmask
        """
        return bin(self._data["smart_lithium_error"])

    def get_balancer_status(self) -> str:
        """
        Return the balancer status
        """
        return BalancerStatus(self._data["balancer_status"]).name


class SmartLithium(Device):
    data_type = SmartLithiumData

    PACKET = Struct(
        "bms_flags" / Int32ul,
        "smart_lithium_error" / Int16ul,
        # cell voltages are 8 7-bit values packed across 7 bytes
        "cell_voltages" / Byte[7],
        # battery voltage = 12 bits
        # balancer status = 4 bits
        "battery_voltage_balancer_status" / Int16ul,
        "battery_temperature" / Int8ul,
    )

    def parse_decrypted(self, decrypted: bytes) -> dict:
        pkt = self.PACKET.parse(decrypted)

        return {
            # TODO: parse BMS flags
            # TODO: parse Lithium error
            "bms_flags": pkt.bms_flags,
            "smart_lithium_error": pkt.smart_lithium_error,
            "cell1_voltage": _convert_cell_voltage(pkt.cell_voltages[0] & 0b01111111),
            "cell2_voltage": _convert_cell_voltage(
                (pkt.cell_voltages[1] & 0b00111111) << 1 | pkt.cell_voltages[0] >> 7
            ),
            "cell3_voltage": _convert_cell_voltage(
                (pkt.cell_voltages[2] & 0b00011111) << 2 | pkt.cell_voltages[1] >> 6
            ),
            "cell4_voltage": _convert_cell_voltage(
                (pkt.cell_voltages[3] & 0b00001111) << 3 | pkt.cell_voltages[2] >> 5
            ),
            "cell5_voltage": _convert_cell_voltage(
                (pkt.cell_voltages[4] & 0b00000111) << 4 | pkt.cell_voltages[3] >> 4
            ),
            "cell6_voltage": _convert_cell_voltage(
                (pkt.cell_voltages[5] & 0b00000011) << 5 | pkt.cell_voltages[4] >> 3
            ),
            "cell7_voltage": _convert_cell_voltage(
                (pkt.cell_voltages[6] & 0b00000001) << 6 | pkt.cell_voltages[5] >> 2
            ),
            "cell8_voltage": _convert_cell_voltage(pkt.cell_voltages[6] >> 1),
            "battery_voltage": (pkt.battery_voltage_balancer_status & 0xFFF) / 100.0,
            "balancer_status": pkt.battery_voltage_balancer_status >> 12,
            "battery_temperature": (pkt.battery_temperature & 0x7F) - 40,
        }
