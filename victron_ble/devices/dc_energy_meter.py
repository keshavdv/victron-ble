from enum import Enum
from typing import Any, Dict, Optional

from construct import BitStruct, Flag, Int8sl, Int16sl, Int16ul, Int24sl, Struct

from victron_ble.devices.base import Device, DeviceData, kelvin_to_celsius
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
    def __init__(self, data: Dict[str, Any]) -> None:
        self._data = data

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

    def get_low_voltage_alarm(self) -> bool:
        """
        Return a boolean indicating if the low voltage alarm is active
        """
        return self._data["alarm"]["low_voltage"]

    def get_high_voltage_alarm(self) -> bool:
        """
        Return a boolean indicating if the high voltage alarm is active
        """
        return self._data["alarm"]["high_voltage"]

    def get_low_starter_battery_voltage_alarm(self) -> bool:
        """
        Return a boolean indicating if the low starter battery voltage alarm is active
        """
        return self._data["alarm"]["low_starter_voltage"]

    def get_high_starter_battery_voltage_alarm(self) -> bool:
        """
        Return a boolean indicating if the high starter battery voltage alarm is active
        """
        return self._data["alarm"]["high_starter_voltage"]

    def get_low_temperature_alarm(self) -> bool:
        """
        Return a boolean indicating if the low temperature alarm is active
        """
        return self._data["alarm"]["low_temperature"]

    def get_high_temperature_alarm(self) -> bool:
        """
        Return a boolean indicating if the high temperature alarm is active
        """
        return self._data["alarm"]["high_temperature"]

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

    PACKET = Struct(
        "meter_type" / Int16sl,
        # Voltage reading in 10mV increments
        "voltage" / Int16ul,
        "alarm"
        / BitStruct(
            "mid_voltage" / Flag,
            "high_temperature" / Flag,
            "low_temperature" / Flag,
            "high_starter_voltage" / Flag,
            "low_starter_voltage" / Flag,
            "low_soc" / Flag,
            "high_voltage" / Flag,
            "low_voltage" / Flag,
        ),
        # Unknown byte
        "uk_1b" / Int8sl,
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

    def parse(self, data: bytes) -> DcEnergyMeterData:
        decrypted = self.decrypt(data)
        pkt = self.PACKET.parse(decrypted)

        aux_mode = AuxMode(pkt.current & 0b11)

        parsed = {
            "meter_type": MeterType(pkt.meter_type),
            "aux_mode": aux_mode,
            "current": (pkt.current >> 2) / 1000,
            "voltage": pkt.voltage / 100,
            "alarm": {
                "low_voltage": pkt.alarm.low_voltage,
                "high_voltage": pkt.alarm.high_voltage,
                "low_starter_voltage": pkt.alarm.low_starter_voltage,
                "high_starter_voltage": pkt.alarm.high_starter_voltage,
                "low_temperature": pkt.alarm.low_temperature,
                "high_temperature": pkt.alarm.high_temperature,
            },
        }

        if aux_mode == AuxMode.STARTER_VOLTAGE:
            # Starter voltage is treated as signed
            parsed["starter_voltage"] = (
                Int16sl.parse((pkt.aux).to_bytes(2, "little")) / 100
            )
        elif aux_mode == AuxMode.TEMPERATURE:
            parsed["temperature_kelvin"] = pkt.aux / 100

        return DcEnergyMeterData(parsed)
