from typing import Any, Dict

from victron_ble.devices import BatteryMonitor, Device


class BatterySenseData:
    def __init__(self, data: Dict[str, Any]) -> None:
        self.data = data

    def get_temperature(self) -> float:
        """
        Return the temperature in celsius
        """
        return self.data["temperature"]

    def get_voltage(self) -> float:
        """
        Return the voltage in volts
        """
        return self.data["voltage"]


class BatterySense(Device):
    def parse(self, data: bytes) -> BatterySenseData:
        parsed = BatteryMonitor(self.advertisement_key).parse(data)

        return BatterySenseData(
            {"temperature": parsed.get_temperature(), "voltage": parsed.get_voltage()}
        )
