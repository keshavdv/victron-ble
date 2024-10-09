from enum import Enum

from construct import Int8ul, Int16sl, Int16ul, Int32ul, Struct

from victron_ble.devices.base import (
    AlarmReason,
    ChargerError,
    Device,
    DeviceData,
    OffReason,
    OperationMode,
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

    def get_output_state(self) -> OutputState:
        """
        Return the output state
        """
        return self._data["output_state"]

    def get_error_code(self) -> ChargerError:
        """
        Return the error code
        """
        return self._data["error_code"]

    def get_alarm_reason(self) -> AlarmReason:
        """
        Return the alarm reason
        """
        return self._data["alarm_reason"]

    def get_warning_reason(self) -> AlarmReason:
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
        "input_voltage" / Int16sl,
        "output_voltage" / Int16ul,
        "off_reason" / Int32ul,
    )

    def parse_decrypted(self, decrypted: bytes) -> dict:
        pkt = self.PACKET.parse(decrypted)

        return {
            "device_state": (
                OperationMode(pkt.device_state) if pkt.device_state != 0xFF else None
            ),
            "output_state": (
                OutputState(pkt.output_state) if pkt.output_state != 0xFF else None
            ),
            "error_code": (
                ChargerError(pkt.error_code) if pkt.error_code != 0xFF else None
            ),
            "alarm_reason": AlarmReason(pkt.alarm_reason),
            "warning_reason": AlarmReason(pkt.warning_reason),
            "input_voltage": (
                pkt.input_voltage / 100 if pkt.input_voltage != 0x7FFF else None
            ),
            "output_voltage": (
                pkt.output_voltage / 100 if pkt.output_voltage != 0xFFFF else None
            ),
            "off_reason": OffReason(pkt.off_reason),
        }
