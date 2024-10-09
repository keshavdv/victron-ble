from enum import Enum

from victron_ble.devices.base import (
    AlarmReason,
    BitReader,
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

    def parse_decrypted(self, decrypted: bytes) -> dict:
        reader = BitReader(decrypted)

        device_state = reader.read_unsigned_int(8)
        output_state = reader.read_unsigned_int(8)
        error_code = reader.read_unsigned_int(8)
        alarm_reason = reader.read_unsigned_int(16)
        warning_reason = reader.read_unsigned_int(16)
        input_voltage = reader.read_signed_int(16)
        output_voltage = reader.read_unsigned_int(16)
        off_reason = reader.read_unsigned_int(32)

        return {
            "device_state": (
                OperationMode(device_state) if device_state != 0xFF else None
            ),
            "output_state": (
                OutputState(output_state) if output_state != 0xFF else None
            ),
            "error_code": (ChargerError(error_code) if error_code != 0xFF else None),
            "alarm_reason": AlarmReason(alarm_reason),
            "warning_reason": AlarmReason(warning_reason),
            "input_voltage": (input_voltage / 100 if input_voltage != 0x7FFF else None),
            "output_voltage": (
                output_voltage / 100 if output_voltage != 0xFFFF else None
            ),
            "off_reason": OffReason(off_reason),
        }
