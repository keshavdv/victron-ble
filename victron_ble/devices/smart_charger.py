from typing import Optional

from victron_ble.devices.base import (
    BitReader,
    ChargerError,
    Device,
    DeviceData,
    OperationMode,
)


class SmartChargerData(DeviceData):
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

    def get_battery_voltage(self) -> Optional[float]:
        """
        Return the battery voltage in volts
        """
        return self._data["battery_voltage"]

    def get_battery_charging_current(self) -> Optional[float]:
        """
        Return the battery charging current in amps
        """
        return self._data["battery_charging_current"]


class SmartCharger(Device):
    data_type = SmartChargerData

    def parse_decrypted(self, decrypted: bytes) -> dict:
        reader = BitReader(decrypted)

        # Charge State:   0 - Off
        #                 3 - Bulk
        #                 4 - Absorption
        #                 5 - Float
        charge_state = reader.read_unsigned_int(8)
        charger_error = reader.read_unsigned_int(8)
        # Battery voltage reading in 0.01V increments
        battery_voltage = reader.read_signed_int(13)
        # Battery charging Current reading in 0.1A increments
        battery_charging_current = reader.read_signed_int(11)

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
        }
