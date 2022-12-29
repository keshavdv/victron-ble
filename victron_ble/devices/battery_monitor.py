from enum import Enum
from typing import Any, Dict, Optional

from construct import (
    BitStruct,
    Flag,
    GreedyBytes,
    Int8sl,
    Int16sl,
    Int16ul,
    Int24sl,
    Struct,
)

from victron_ble.devices.base import Device, DeviceData, kelvin_to_celsius


class AuxMode(Enum):
    STARTER_VOLTAGE = 0
    MIDPOINT_VOLTAGE = 1
    TEMPERATURE = 2
    DISABLED = 3


class BatteryMonitorData(DeviceData):
    def __init__(self, data: Dict[str, Any]) -> None:
        self._data = data

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

    def get_low_soc_alarm(self) -> bool:
        """
        Return a boolean indicating if the low state of charge alarm is active
        """
        return self._data["alarm"]["low_soc"]

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

    def get_midpoint_deviation_alarm(self) -> bool:
        """
        Return a boolean indicating if the high temperature alarm is active
        """
        return self._data["alarm"]["mid_deviation"]

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

    PACKET = Struct(
        # Remaining time in minutes
        "remaining_mins" / Int16ul,
        # Voltage reading in 10mV increments
        "voltage" / Int16ul,
        # Bit map of alarm status
        # 0b00000001 = low voltage alarm
        # 0b00000010 = high voltage alarm
        # 0b00000100 = low soc alarm
        # 0b00001000 = low starter alarm
        # 0b00001001 = low voltage + low starter alarm
        # 0b00011001 = high starter + low voltage + low starter alarm
        # 0b00010000 = high starter alarm
        # 0b00100000 = low temp alarm
        # 0b01000000 = high temp alarm
        # 0b10000000 = midpoint voltage deviation alarm
        "alarm"
        / BitStruct(
            "mid_deviation" / Flag,
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
        # Value of the auxillary input (millivolts or degrees)
        "aux" / Int16ul,
        # The upper 22 bits indicate the current in milliamps
        # The lower 2 bits identify the aux input mode:
        #   0 = Starter battery voltage
        #   1 = Midpoint voltage
        #   2 = Temperature
        #   3 = Disabled
        "current" / Int24sl,
        # Consumed Ah in 0.1Ah increments
        "consumed_ah" / Int16ul,
        # The lowest 4 bits are unknown
        # The next 8 bits indicate the state of charge in 0.1% increments
        # The upper 2 bits are unknown
        "soc" / Int16ul,
        # Throw away any extra bytes
        GreedyBytes,
    )

    def parse(self, data: bytes) -> BatteryMonitorData:
        decrypted = self.decrypt(data)
        pkt = self.PACKET.parse(decrypted)

        aux_mode = AuxMode(pkt.current & 0b11)

        parsed = {
            "remaining_mins": pkt.remaining_mins,
            "aux_mode": aux_mode,
            "current": (pkt.current >> 2) / 1000,
            "voltage": pkt.voltage / 100,
            "consumed_ah": pkt.consumed_ah / 10,
            "soc": ((pkt.soc & 0x3FFF) >> 4) / 10,
            "alarm": {
                "low_voltage": pkt.alarm.low_voltage,
                "high_voltage": pkt.alarm.high_voltage,
                "low_soc": pkt.alarm.low_soc,
                "low_starter_voltage": pkt.alarm.low_starter_voltage,
                "high_starter_voltage": pkt.alarm.high_starter_voltage,
                "low_temperature": pkt.alarm.low_temperature,
                "high_temperature": pkt.alarm.high_temperature,
                "mid_deviation": pkt.alarm.mid_deviation,
            },
        }

        if aux_mode == AuxMode.STARTER_VOLTAGE:
            # Starter voltage is treated as signed
            parsed["starter_voltage"] = (
                Int16sl.parse((pkt.aux).to_bytes(2, "little")) / 100
            )
        elif aux_mode == AuxMode.MIDPOINT_VOLTAGE:
            parsed["midpoint_voltage"] = pkt.aux / 100
        elif aux_mode == AuxMode.TEMPERATURE:
            parsed["temperature_kelvin"] = pkt.aux / 100

        return BatteryMonitorData(parsed)
