from victron_ble.devices.base import DeviceData, kelvin_to_celsius
from victron_ble.devices.battery_monitor import BatteryMonitor


class BatterySenseData(DeviceData):
    def get_temperature(self) -> float:
        """
        Return the temperature in Celsius
        """
        return kelvin_to_celsius(self._data["temperature_kelvin"])

    def get_voltage(self) -> float:
        """
        Return the voltage in volts
        """
        return self._data["voltage"]


class BatterySense(BatteryMonitor):
    data_type = BatterySenseData
