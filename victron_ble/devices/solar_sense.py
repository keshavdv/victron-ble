from typing import Optional

from victron_ble.devices.base import BitReader, Device, DeviceData


class SolarSenseData(DeviceData):
    def get_installation_power(self) -> Optional[int]:
        """Return the estimated solar installation power in watts."""
        return self._data["installation_power"]

    def get_yield_today(self) -> Optional[int]:
        """Return today's yield in watt-hours."""
        return self._data["yield_today"]

    def get_irradiance(self) -> Optional[float]:
        """Return solar irradiance in watts per square meter."""
        return self._data["irradiance"]

    def get_cell_temperature(self) -> Optional[float]:
        """Return panel temperature in degrees Celsius."""
        return self._data["cell_temperature"]


class SolarSense(Device):
    data_type = SolarSenseData

    def parse(self, data: bytes) -> SolarSenseData:
        """Parse a plaintext SolarSense advertisement."""
        if len(data) < 24:
            raise ValueError("SolarSense advertisement is incomplete")
        model_id = self.get_model_id(data)
        return self.data_type(model_id, self.parse_decrypted(data[8:]))

    def parse_decrypted(self, decrypted: bytes) -> dict:
        """Parse the packed SolarSense data fields."""
        reader = BitReader(decrypted)
        reader.read_unsigned_int(32)
        reader.read_unsigned_int(8)
        installation_power = reader.read_unsigned_int(20)
        yield_today = reader.read_unsigned_int(20)
        irradiance = reader.read_unsigned_int(14)
        cell_temperature = reader.read_unsigned_int(11)
        reader.read_unsigned_int(1)
        reader.read_unsigned_int(8)
        reader.read_unsigned_int(1)
        reader.read_unsigned_int(7)

        return {
            "installation_power": (
                installation_power if installation_power != 0xFFFFF else None
            ),
            "yield_today": yield_today * 10 if yield_today != 0xFFFFF else None,
            "irradiance": irradiance / 10 if irradiance != 0x3FFF else None,
            "cell_temperature": (
                cell_temperature / 10 - 60 if cell_temperature != 0x7FF else None
            ),
        }
