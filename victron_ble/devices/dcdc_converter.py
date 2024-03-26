from victron_ble.devices.base import (
    BitReader,
    ChargerError,
    Device,
    DeviceData,
    OffReason,
    OperationMode,
)


class DcDcConverterData(DeviceData):
    def get_charge_state(self) -> OperationMode:
        """
        Return an enum indicating the current charging state
        """
        return self._data["device_state"]

    def get_charger_error(self) -> ChargerError:
        """
        Return an enum indicating the error code
        """
        return self._data["charger_error"]

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

    def get_off_reason(self) -> OffReason:
        """
        Return an error code stating the reason for the output to be off
        """
        return self._data["off_reason"]


class DcDcConverter(Device):
    data_type = DcDcConverterData

    def parse_decrypted(self, decrypted: bytes) -> dict:
        reader = BitReader(decrypted)

        # Charge State:   0 - Off
        #                 3 - Bulk
        #                 4 - Absorption
        #                 5 - Float
        device_state = reader.read_unsigned_int(8)
        # Charger Error Code
        charger_error = reader.read_unsigned_int(8)
        # Input voltage reading in 0.01V increments
        input_voltage = reader.read_unsigned_int(16)
        # Output voltage in 0.01V
        output_voltage = reader.read_signed_int(16)
        # Reason for Charger Off
        off_reason = reader.read_unsigned_int(32)

        return {
            "device_state": (
                OperationMode(device_state) if device_state != 0xFF else None
            ),
            "charger_error": (
                ChargerError(charger_error) if charger_error != 0xFF else None
            ),
            "input_voltage": input_voltage / 100 if input_voltage != 0xFFFF else None,
            "output_voltage": (
                output_voltage / 100 if output_voltage != 0x7FFF else None
            ),
            "off_reason": OffReason(off_reason),
        }
