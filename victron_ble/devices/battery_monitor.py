from enum import Enum
from typing import Optional, Type

from victron_ble.devices.base import (
    AlarmReason,
    BitReader,
    Device,
    DeviceData,
    kelvin_to_celsius,
)


class AuxMode(Enum):
    STARTER_VOLTAGE = 0
    MIDPOINT_VOLTAGE = 1
    TEMPERATURE = 2
    DISABLED = 3


class BatteryMonitorData(DeviceData):
    def get_remaining_mins(self) -> float:
        """
        Return the number of remaining minutes of battery life in minutes
        """
        return self._data["remaining_mins"]

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

    def get_alarm(self) -> AlarmReason:
        """
        Return an enum indicating the current alarm reason
        """
        return self._data["alarm"]

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

    def get_midpoint_voltage(self) -> Optional[float]:
        """
        Return the midpoint battery voltage in volts if the aux input is set to midpoint voltage
        """
        return self._data.get("midpoint_voltage")


class BatteryMonitor(Device):
    data_type: Type[DeviceData] = BatteryMonitorData

    def parse_decrypted(self, decrypted: bytes) -> dict:
        reader = BitReader(decrypted)

        # Remaining time in minutes
        remaining_mins = reader.read_unsigned_int(16)
        # Voltage reading in 10mV increments
        voltage = reader.read_signed_int(16)
        # Alarm reason
        alarm = reader.read_unsigned_int(16)
        # Value of the auxillary input (millivolts or degrees)
        aux = reader.read_unsigned_int(16)
        aux_mode = reader.read_unsigned_int(2)
        # The current in milliamps
        current = reader.read_signed_int(22)
        # Consumed Ah in 0.1Ah increments
        consumed_ah = reader.read_unsigned_int(20)
        # The state of charge in 0.1% increments
        soc = reader.read_unsigned_int(10)

        parsed = {
            "remaining_mins": remaining_mins if remaining_mins != 0xFFFF else None,
            "voltage": voltage / 100 if voltage != 0x7FFF else None,
            "alarm": AlarmReason(alarm),
            "aux_mode": AuxMode(aux_mode),
            "current": current / 1000 if current != 0x3FFFFF else None,
            "consumed_ah": -consumed_ah / 10 if consumed_ah != 0xFFFFF else None,
            "soc": soc / 10 if soc != 0x3FF else None,
        }

        if aux_mode == AuxMode.STARTER_VOLTAGE.value:
            # Starter voltage is treated as signed
            parsed["starter_voltage"] = BitReader.to_signed_int(aux, 16) / 100
        elif aux_mode == AuxMode.MIDPOINT_VOLTAGE.value:
            parsed["midpoint_voltage"] = aux / 100
        elif aux_mode == AuxMode.TEMPERATURE.value:
            parsed["temperature_kelvin"] = aux / 100

        return parsed
