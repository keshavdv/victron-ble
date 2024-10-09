from enum import Enum
from typing import Optional

from victron_ble.devices.base import (
    AlarmReason,
    BitReader,
    Device,
    DeviceData,
    kelvin_to_celsius,
)
from victron_ble.devices.battery_monitor import AuxMode


class MeterType(Enum):
    SOLAR_CHARGER = -9
    WIND_CHARGER = -8
    SHAFT_GENERATOR = -7
    ALTERNATOR = -6
    FUEL_CELL = -5
    WATER_GENERATOR = -4
    DC_DC_CHARGER = -3
    AC_CHARGER = -2
    GENERIC_SOURCE = -1
    GENERIC_LOAD = 1
    ELECTRIC_DRIVE = 2
    FRIDGE = 3
    WATER_PUMP = 4
    BILGE_PUMP = 5
    DC_SYSTEM = 6
    INVERTER = 7
    WATER_HEATER = 8


class DcEnergyMeterData(DeviceData):
    def get_meter_type(self) -> MeterType:
        """
        Return an enum indicating the current meter type
        """
        return self._data["meter_type"]

    def get_current(self) -> float:
        """
        Return the current in amps
        """
        return self._data["current"]

    def get_voltage(self) -> float:
        """
        Return the voltage in volts
        """
        return self._data["voltage"]

    def get_alarm(self) -> Optional[AlarmReason]:
        """
        Return an enum indicating the current alarm reason or None otherwise
        """
        return AlarmReason(self._data["alarm"]) if self._data["alarm"] > 0 else None

    def get_aux_mode(self) -> AuxMode:
        """
        Return an enum indicating the current auxiliary input mode
        """
        return self._data["aux_mode"]

    def get_temperature(self) -> Optional[float]:
        """
        Return the temperature in Celsius if the aux input is set to temperature
        """
        temp = self._data.get("temperature_kelvin")
        if temp:
            return kelvin_to_celsius(temp)
        return None

    def get_starter_voltage(self) -> Optional[float]:
        """
        Return the starter battery voltage in volts if the aux input is set to starter battery
        """
        return self._data.get("starter_voltage")


class DcEnergyMeter(Device):
    data_type = DcEnergyMeterData

    def parse_decrypted(self, decrypted: bytes) -> dict:
        reader = BitReader(decrypted)

        meter_type = reader.read_signed_int(16)
        # Voltage reading in 10mV increments
        voltage = reader.read_signed_int(16)
        # Alarm reason
        alarm = reader.read_unsigned_int(16)
        # Value of the auxillary input
        aux = reader.read_unsigned_int(16)
        # The aux input mode:
        #   0 = Starter battery voltage
        #   2 = Temperature
        #   3 = Disabled
        aux_mode = reader.read_unsigned_int(2)
        # The current in milliamps
        current = reader.read_signed_int(22)

        parsed = {
            "meter_type": MeterType(meter_type),
            "aux_mode": AuxMode(aux_mode),
            "current": current / 1000 if current != 0x3FFFFF else None,
            "voltage": voltage / 100 if voltage != 0x7FFF else None,
            "alarm": alarm,
        }

        if aux_mode == AuxMode.STARTER_VOLTAGE.value:
            # Starter voltage is treated as signed
            parsed["starter_voltage"] = BitReader.to_signed_int(aux, 16) / 100
        elif aux_mode == AuxMode.TEMPERATURE.value:
            if aux == 0xFFFF:
                parsed["temperature_kelvin"] = None
            else:
                parsed["temperature_kelvin"] = aux / 100

        return parsed
