from typing import Optional

from victron_ble.devices.base import (
    BitReader,
    ChargerError,
    Device,
    DeviceData,
    OperationMode,
)


class AcChargerData(DeviceData):
    def get_charge_state(self) -> Optional[OperationMode]:
        """
        Return an enum indicating the current charging state
        """
        return self._data["charge_state"]

    def get_charger_error(self) -> Optional[ChargerError]:
        """
        Return an enum indicating the current charging error
        """
        return self._data["charger_error"]

    def get_output_voltage1(self) -> Optional[float]:
        """
        Return the output voltage in volts
        """
        return self._data["output_voltage1"]

    def get_output_voltage2(self) -> Optional[float]:
        """
        Return the output voltage in volts
        """
        return self._data["output_voltage2"]

    def get_output_voltage3(self) -> Optional[float]:
        """
        Return the output voltage in volts
        """
        return self._data["output_voltage3"]

    def get_output_current1(self) -> Optional[float]:
        """
        Return the output charging current in amps
        """
        return self._data["output_current1"]

    def get_output_current2(self) -> Optional[float]:
        """
        Return the output charging current in amps
        """
        return self._data["output_current2"]

    def get_output_current3(self) -> Optional[float]:
        """
        Return the output charging current in amps
        """
        return self._data["output_current3"]

    def get_temperature(self) -> Optional[float]:
        """
        Return the temperature of the charger in celcius
        """
        return self._data["temperature"]

    def get_ac_current(self) -> Optional[float]:
        """
        Return the input current in amps
        """
        return self._data["ac_current"]


class AcCharger(Device):
    data_type = AcChargerData

    def parse_decrypted(self, decrypted: bytes) -> dict:
        reader = BitReader(decrypted)

        # Charge State:   0 - Off
        #                 3 - Bulk
        #                 4 - Absorption
        #                 5 - Float
        charge_state = reader.read_unsigned_int(8)
        charger_error = reader.read_unsigned_int(8)
        output_voltage1 = reader.read_unsigned_int(
            13
        )  # Output voltage reading in 0.01V increments
        output_current1 = reader.read_unsigned_int(
            11
        )  # Output current reading in 0.1A increments
        output_voltage2 = reader.read_unsigned_int(13)
        output_current2 = reader.read_unsigned_int(11)
        output_voltage3 = reader.read_unsigned_int(13)
        output_current3 = reader.read_unsigned_int(11)
        temerature = reader.read_unsigned_int(7)  # Celsius
        ac_current = reader.read_unsigned_int(
            9
        )  # AC current reading in 0.1A increments

        return {
            "charge_state": (
                OperationMode(charge_state) if charge_state != 0xFF else None
            ),
            "charger_error": (
                ChargerError(charger_error) if charger_error != 0xFF else None
            ),
            "output_voltage1": (
                output_voltage1 / 100 if output_voltage1 != 0x1FFF else None
            ),
            "output_voltage2": (
                output_voltage2 / 100 if output_voltage2 != 0x1FFF else None
            ),
            "output_voltage3": (
                output_voltage3 / 100 if output_voltage3 != 0x1FFF else None
            ),
            "output_current1": (
                output_current1 / 10 if output_current1 != 0x7FF else None
            ),
            "output_current2": (
                output_current2 / 10 if output_current2 != 0x7FF else None
            ),
            "output_current3": (
                output_current3 / 10 if output_current3 != 0x7FF else None
            ),
            "temperature": ((temerature - 40) if temerature != 0x7F else None),
            "ac_current": (ac_current / 10 if ac_current != 0x1FF else None),
        }
