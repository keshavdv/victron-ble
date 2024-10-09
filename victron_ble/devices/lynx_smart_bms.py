from victron_ble.devices.base import BitReader, Device, DeviceData


class LynxSmartBMSData(DeviceData):
    def get_error_flags(self) -> int:
        """
        Get the raw error_flags field (meaning not documented).
        """
        return self._data["error_flags"]

    def get_remaining_mins(self) -> float:
        """
        Return the number of remaining minutes of battery life in minutes
        """
        return self._data["remaining_mins"]

    def get_voltage(self) -> float:
        """
        Return the voltage in volts
        """
        return self._data["voltage"]

    def get_current(self) -> float:
        """
        Return the current in amps
        """
        return self._data["current"]

    def get_io_status(self) -> int:
        """
        Get the raw io_status field (meaning not documented).
        """
        return self._data["io_status"]

    def get_alarm_flags(self) -> int:
        """
        Get the raw alarm_flags field (meaning not documented).
        """
        return self._data["alarm_flags"]

    def get_soc(self) -> float:
        """
        Return the state of charge in percentage
        """
        return self._data["soc"]

    def get_consumed_ah(self) -> float:
        """
        Return the consumed energy in amp hours
        """
        return self._data["consumed_ah"]

    def get_battery_temperature(self) -> int:
        """
        Return the temperature in Celsius if the aux input is set to temperature
        """
        return self._data["battery_temperature"]


class LynxSmartBMS(Device):
    data_type = LynxSmartBMSData

    def parse_decrypted(self, decrypted: bytes) -> dict:

        reader = BitReader(decrypted)
        error_flags = reader.read_unsigned_int(8)
        remaining_mins = reader.read_unsigned_int(16)
        voltage = reader.read_signed_int(16)
        current = reader.read_signed_int(16)
        io_status = reader.read_unsigned_int(16)
        alarm_flags = reader.read_unsigned_int(18)
        soc = reader.read_unsigned_int(10)
        consumed_ah = reader.read_unsigned_int(20)
        temperature = reader.read_unsigned_int(7)

        parsed = {
            "error_flags": error_flags,
            "remaining_mins": (remaining_mins if remaining_mins != 0xFFFF else None),
            "voltage": voltage / 100 if voltage != 0x7FFF else None,
            "current": current / 10 if current != 0x7FFF else None,
            "io_status": io_status,
            "alarm_flags": alarm_flags,
            "soc": soc / 10.0 if soc != 0x3FFF else None,
            "consumed_ah": consumed_ah / 10 if consumed_ah != 0xFFFFF else None,
            "battery_temperature": (
                (temperature - 40) if temperature != 0x7F else None
            ),
        }

        return parsed
