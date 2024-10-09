from typing import Optional

from victron_ble.devices.base import (
    BitReader,
    ChargerError,
    Device,
    DeviceData,
    OperationMode,
)


class SolarChargerData(DeviceData):
    def get_charge_state(self) -> OperationMode:
        """
        Return an enum indicating the current charging state
        """
        return self._data["charge_state"]

    def get_charger_error(self) -> ChargerError:
        """
        Return an enum indicating the current charging error
        """
        return self._data["charger_error"]

    def get_battery_voltage(self) -> float:
        """
        Return the battery voltage in volts
        """
        return self._data["battery_voltage"]

    def get_battery_charging_current(self) -> float:
        """
        Return the battery charging current in amps
        """
        return self._data["battery_charging_current"]

    def get_yield_today(self) -> float:
        """
        Return the yield_today in Wh
        """
        return self._data["yield_today"]

    def get_solar_power(self) -> float:
        """
        Return the current solar power in W
        """
        return self._data["solar_power"]

    def get_external_device_load(self) -> Optional[float]:
        """
        Return the external device load in amps
        """
        return self._data["external_device_load"]


class SolarCharger(Device):
    data_type = SolarChargerData

    def parse_decrypted(self, decrypted: bytes) -> dict:
        reader = BitReader(decrypted)

        # Charge State:   0 - Off
        #                 3 - Bulk
        #                 4 - Absorption
        #                 5 - Float
        charge_state = reader.read_unsigned_int(8)
        charger_error = reader.read_unsigned_int(8)
        # Battery voltage reading in 0.01V increments
        battery_voltage = reader.read_signed_int(16)
        # Battery charging Current reading in 0.1A increments
        battery_charging_current = reader.read_signed_int(16)
        # Todays solar power yield in 10Wh increments
        yield_today = reader.read_unsigned_int(16)
        # Current power from solar in 1W increments
        solar_power = reader.read_unsigned_int(16)
        # External device load in 0.1A increments
        external_device_load = reader.read_unsigned_int(9)

        return {
            "charge_state": (
                OperationMode(charge_state) if charge_state != 0xFF else None
            ),
            "charger_error": (
                ChargerError(charger_error) if charger_error != 0xFF else None
            ),
            "battery_voltage": (
                battery_voltage / 100 if battery_voltage != 0x7FFF else None
            ),
            "battery_charging_current": (
                battery_charging_current / 10
                if battery_charging_current != 0x7FFF
                else None
            ),
            "yield_today": yield_today * 10 if yield_today != 0xFFFF else None,
            "solar_power": solar_power if solar_power != 0xFFFF else None,
            "external_device_load": (
                external_device_load / 10 if external_device_load != 0x1FF else None
            ),
        }
