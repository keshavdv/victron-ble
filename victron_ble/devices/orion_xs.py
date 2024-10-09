from victron_ble.devices.base import (
    BitReader,
    ChargerError,
    Device,
    DeviceData,
    OffReason,
    OperationMode,
)


class OrionXSData(DeviceData):
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

    def get_input_current(self) -> float:
        """
        Return the input current in amps
        """
        return self._data["input_current"]

    def get_output_voltage(self) -> float:
        """
        Return the output voltage in volts
        """
        return self._data["output_voltage"]

    def get_output_current(self) -> float:
        """
        Return the output current in amps
        """
        return self._data["output_current"]

    def get_off_reason(self) -> OffReason:
        """
        Return an error code stating the reason for the output to be off
        """
        return self._data["off_reason"]


class OrionXS(Device):
    data_type = OrionXSData

    # Based on reverse engineering by Fabian Schmidt.
    # The record format has not been documented by Victron as of when this was implemented.
    # See https://github.com/Fabian-Schmidt/esphome-victron_ble/pull/54
    def parse_decrypted(self, decrypted: bytes) -> dict:
        reader = BitReader(decrypted)

        # Charge State:   0 - Off
        #                 3 - Bulk
        #                 4 - Absorption
        #                 5 - Float
        device_state = reader.read_unsigned_int(8)
        # Charger Error Code
        charger_error = reader.read_unsigned_int(8)
        # Output voltage in 0.01V
        output_voltage = reader.read_unsigned_int(16)
        # Output current in 0.1A
        output_current = reader.read_unsigned_int(16)
        # Input voltage reading in 0.01V increments
        input_voltage = reader.read_unsigned_int(16)
        # Input current in 0.1A
        input_current = reader.read_unsigned_int(16)
        # Reason for Charger Off
        off_reason = reader.read_unsigned_int(32)

        return {
            "device_state": (
                OperationMode(device_state) if device_state != 0xFF else None
            ),
            "charger_error": (
                ChargerError(charger_error) if charger_error != 0xFF else None
            ),
            "output_voltage": (
                output_voltage / 100 if output_voltage != 0xFFFF else None
            ),
            "output_current": output_current / 10 if output_current != 0xFFFF else None,
            "input_voltage": input_voltage / 100 if input_voltage != 0xFFFF else None,
            "input_current": input_current / 10 if input_current != 0xFFFF else None,
            "off_reason": OffReason(off_reason),
        }
