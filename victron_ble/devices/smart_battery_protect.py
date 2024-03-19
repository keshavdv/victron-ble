from construct import Struct, Int8ul, Int16ul, Int32ul
from enum import Enum

from victron_ble.devices.base import (
    AlarmReason,
    ChargerError,
    Device,
    DeviceData,
    OperationMode,
    OffReason,
)


class OutputState(Enum):
    ON = 1
    OFF = 4


class SmartBatteryProtectData(DeviceData):
    def get_device_state(self) -> OperationMode:
        """
        Return the device state
        """
        return self._data["device_state"]

    def get_output_state(self) -> int:
        """
        Return the output state
        """
        return self._data["output_state"]

    def get_error_code(self) -> int:
        """
        Return the error code
        """
        return self._data["error_code"]

    def get_alarm_reason(self) -> int:
        """
        Return the alarm reason
        """
        return self._data["alarm_reason"]

    def get_warning_reason(self) -> int:
        """
        Return the warning reason
        """
        return self._data["warning_reason"]

    def get_input_voltage(self) -> float:
        """
        Return the input voltage in volts
        """
        return self._data["input_voltage"]

    def get_output_voltage(self) -> float:
        """
        Return the output voltage in volts
        """
        return self._data["output_voltage"]

    def get_off_reason(self) -> int:
        """
        Return the off reason
        """
        return self._data["off_reason"]


class SmartBatteryProtect(Device):
    data_type = SmartBatteryProtectData

    PACKET = Struct(
        "device_state" / Int8ul,
        "output_state" / Int8ul,
        "error_code" / Int8ul,
        "alarm_reason" / Int16ul,
        "warning_reason" / Int16ul,
        "input_voltage" / Int16ul,
        "output_voltage" / Int16ul,
        "off_reason" / Int32ul,
    )

    def parse_decrypted(self, decrypted: bytes) -> dict:
        pkt = self.PACKET.parse(decrypted)

        return {
            "device_state": OperationMode(pkt.device_state),
            "output_state": OutputState(pkt.output_state),
            "error_code": ChargerError(pkt.error_code),
            "alarm_reason": AlarmReason(pkt.alarm_reason),
            "warning_reason": AlarmReason(pkt.warning_reason),
            "input_voltage": pkt.input_voltage / 100,
            "output_voltage": pkt.output_voltage / 100,
            "off_reason": OffReason(pkt.off_reason),
        }
