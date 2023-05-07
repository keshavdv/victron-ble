from enum import Enum
from typing import Optional

from construct import Int16sl, Int16ul, Int24sl, Struct

from victron_ble.devices.base import AlarmReason, Device, DeviceData, kelvin_to_celsius
from victron_ble.devices.battery_monitor import AuxMode


class MeterType(Enum):
    SOLAR_CHARGER = -7
    WIND_CHARGER = -6
    SHAFT_GENERATOR = -5
    ALTERNATOR = -4
    FUEL_CELL = -3
    WATER_GENERATOR = -2
    DC_DC_CHARGER = -1
    AC_CHARGER = 1
    GENERIC_SOURCE = 2
    GENERIC_LOAD = 3
    ELECTRIC_DRIVE = 4
    FRIDGE = 5
    WATER_PUMP = 6
    BILGE_PUMP = 7
    DC_SYSTEM = 8
    INVERTER = 9
    WATER_HEATER = 10


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

    PACKET = Struct(
        "meter_type" / Int16sl,
        # Voltage reading in 10mV increments
        "voltage" / Int16ul,
        # Alarm reason
        "alarm" / Int16ul,
        # Value of the auxillary input
        "aux" / Int16ul,
        # The upper 22 bits indicate the current in milliamps
        # The lower 2 bits identify the aux input mode:
        #   0 = Starter battery voltage
        #   1 = Midpoint voltage
        #   2 = Temperature
        #   3 = Disabled
        "current" / Int24sl,
    )

    def parse_decrypted(self, decrypted: bytes) -> dict:
        pkt = self.PACKET.parse(decrypted)

        aux_mode = AuxMode(pkt.current & 0b11)

        parsed = {
            "meter_type": MeterType(pkt.meter_type),
            "aux_mode": aux_mode,
            "current": (pkt.current >> 2) / 1000,
            "voltage": pkt.voltage / 100,
            "alarm": pkt.alarm,
        }

        if aux_mode == AuxMode.STARTER_VOLTAGE:
            # Starter voltage is treated as signed
            parsed["starter_voltage"] = (
                Int16sl.parse((pkt.aux).to_bytes(2, "little")) / 100
            )
        elif aux_mode == AuxMode.TEMPERATURE:
            parsed["temperature_kelvin"] = pkt.aux / 100

        return parsed
