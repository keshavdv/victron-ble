from enum import Enum
from typing import Any, Dict

from construct import Int16sl, Int16ul, Struct

from victron_ble.devices.base import Device, DeviceData


class ChargeState(Enum):
    OFF = 0
    BULK = 3
    ABSORPTION = 4
    FLOAT = 5


class SolarChargerData(DeviceData):
    def __init__(self, data: Dict[str, Any]) -> None:
        self._data = data

    def get_charge_state(self) -> ChargeState:
        """
        Return an enum indicating the current meter type
        """
        return self._data["charge_state"]

    def get_voltage(self) -> float:
        """
        Return the voltage in volts
        """
        return self._data["voltage"]

    def get_current(self) -> float:
        """
        Return the current in amps
        """
        return self._data["current"]

    def get_yield_today(self) -> float:
        """
        Return the yield_today in Wh
        """
        return self._data["yield_today"]

    def get_power(self) -> float:
        """
        Return the current solar power in W
        """
        return self._data["power"]

    def get_load(self) -> float:
        """
        Return the load in amps
        """
        return self._data["load"]


class SolarCharger(Device):

    PACKET = Struct(
        # state:    0 - Off
        #           3 - Bulk
        #           4 - Absorption
        #           5 - Float
        "charge_state" / Int16sl,
        # Voltage reading in 0.01V increments
        "voltage" / Int16ul,
        # Current reading in 0.1A increments
        "current" / Int16ul,
        # Todays solar power yield in 10Wh increments
        "yield_today" / Int16ul,
        # Current power from solar in 1W increments
        "power" / Int16ul,
        # Current load output
        "load" / Int16ul,
    )

    def parse(self, data: bytes) -> SolarChargerData:
        decrypted = self.decrypt(data)
        pkt = self.PACKET.parse(decrypted)

        parsed = {
            "charge_state": ChargeState(pkt.charge_state),
            "voltage": pkt.voltage / 100,
            "current": pkt.current / 10,
            "yield_today": pkt.yield_today * 10,
            "power": pkt.power,
            "load": (pkt.load & 0x01ff)
        }

        return SolarChargerData(parsed)
