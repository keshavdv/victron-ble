from enum import Enum
from typing import Optional

from construct import GreedyBytes, Int16sl, Int16ul, Int24sl, Struct

from victron_ble.devices.base import AlarmReason, Device, DeviceData, kelvin_to_celsius


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
        # Alarm reason
        "alarm" / Int16ul,
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
            "alarm": pkt.alarm,
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

        return BatteryMonitorData(self.get_model_id(data), parsed)
