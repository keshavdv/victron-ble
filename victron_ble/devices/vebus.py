from victron_ble.devices.base import (
    ACInState,
    AlarmNotification,
    BitReader,
    Device,
    DeviceData,
    OperationMode,
)


class VEBusData(DeviceData):
    def get_device_state(self) -> OperationMode:
        """
        Return an enum indicating the device state
        """
        return self._data["device_state"]

    def get_error(self) -> int:
        """
        Return the VEBus error state (unknown interpretation)
        """
        return self._data["error"]

    def get_alarm(self) -> AlarmNotification:
        """
        Return the VEBus alarm state
        """
        return self._data["alarm"]

    def get_ac_in_state(self) -> ACInState:
        """
        Return an enum indicating the current ac power state
        """
        return self._data["ac_in_state"]

    def get_ac_in_power(self) -> float:
        """
        Return the current AC power draw
        """
        return self._data["ac_in_power"]

    def get_ac_out_power(self) -> float:
        """
        Return the current AC power output
        """
        return self._data["ac_out_power"]

    def get_battery_current(self) -> float:
        """
        Return the battery current in amps (positive for charging, negative for inverting)
        """
        return self._data["battery_current"]

    def get_battery_voltage(self) -> float:
        """
        Return the battery voltage in volts
        """
        return self._data["battery_voltage"]

    def get_battery_temperature(self) -> float:
        """
        Return the battery temperature in degrees celcius
        """
        return self._data["battery_temperature"]

    def get_soc(self) -> float:
        """
        Return the battery state of charge as a percentage
        """
        return self._data["soc"]


class VEBus(Device):
    data_type = VEBusData

    def parse_decrypted(self, decrypted: bytes) -> dict:
        reader = BitReader(decrypted)

        # Device state
        device_state = reader.read_unsigned_int(8)
        # VE.Bus error (docs do not explain how to interpret)
        error = reader.read_unsigned_int(8)
        # Battery charging Current reading in 0.1A increments
        battery_current = reader.read_signed_int(16)
        # Battery voltage reading in 0.01V increments (14 bits)
        # Active AC in state (enum) (2 bits)
        battery_voltage = reader.read_unsigned_int(14)
        # AC input active
        ac_in_state = reader.read_unsigned_int(2)
        # Active AC in power in 1W increments (19 bits, signed)
        ac_in_power = reader.read_signed_int(19)
        # AC out power in 1W increments (19 bits, signed)
        ac_out_power = reader.read_signed_int(19)
        # Alarm (enum but docs say "to be defined") (2 bits)
        alarm = reader.read_unsigned_int(2)
        # Battery temperature in 1 degree celcius increments (7 bits)
        battery_temperature = reader.read_unsigned_int(7)
        # Battery state of charge in 1% increments (7 bits)
        soc = reader.read_unsigned_int(7)

        return {
            "device_state": (
                OperationMode(device_state) if device_state != 0xFF else None
            ),
            "error": error if error != 0xFF else None,
            "battery_voltage": (
                battery_voltage / 100 if battery_voltage != 0x3FFF else None
            ),
            "battery_current": (
                battery_current / 10 if battery_current != 0x7FFF else None
            ),
            "ac_in_state": ACInState(ac_in_state) if ac_in_state != 3 else None,
            "ac_in_power": ac_in_power if ac_in_power != 0x3FFFF else None,
            "ac_out_power": ac_out_power if ac_out_power != 0x3FFFF else None,
            "alarm": (AlarmNotification(alarm) if alarm != 3 else None),
            "battery_temperature": (
                battery_temperature - 40 if battery_temperature != 0x7F else None
            ),
            "soc": soc if soc != 0x7F else None,
        }
