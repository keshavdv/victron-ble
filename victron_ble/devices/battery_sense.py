from victron_ble.devices import BatteryMonitor, Device, DeviceData


class BatterySenseData(DeviceData):
    def get_temperature(self) -> float:
        """
        Return the temperature in Celsius
        """
        return self._data["temperature"]

    def get_voltage(self) -> float:
        """
        Return the voltage in volts
        """
        return self._data["voltage"]


class BatterySense(Device):
    def parse(self, data: bytes) -> BatterySenseData:
        parsed = BatteryMonitor(self.advertisement_key).parse(data)

        return BatterySenseData(
            self.get_model_id(data),
            {"temperature": parsed.get_temperature(), "voltage": parsed.get_voltage()},
        )
