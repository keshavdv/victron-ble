from victron_ble.devices.battery_monitor import AuxMode
from victron_ble.devices.dc_energy_meter import (
    DcEnergyMeter,
    DcEnergyMeterData,
    MeterType,
)


class TestDcEnergyMeter:
    def test_end_to_end_parse(self) -> None:
        data = "100289a30d787fafde83ccec982199fd815286"
        actual = DcEnergyMeter("aff4d0995b7d1e176c0c33ecb9e70dcd").parse(
            bytes.fromhex(data)
        )

        assert isinstance(actual, DcEnergyMeterData)
        assert actual.get_meter_type() == MeterType.DC_DC_CHARGER
        assert actual.get_aux_mode() == AuxMode.STARTER_VOLTAGE
        assert actual.get_current() == 0.0
        assert actual.get_voltage() == 12.52
        assert actual.get_starter_voltage() == -0.01

        assert actual.get_alarm() == None

        assert actual.get_temperature() == None
        assert actual.get_model_name() == "SmartShunt 500A/50mV"

    def parse_decrypted(self, decrypted: str) -> DcEnergyMeterData:
        parsed = DcEnergyMeter(None).parse_decrypted(bytes.fromhex(decrypted))
        return DcEnergyMeterData(None, parsed)

    def test_parse(self) -> None:
        actual = self.parse_decrypted("fdffe4040000ffff00000059a65a1c8c")
        assert actual.get_meter_type() == MeterType.DC_DC_CHARGER
        assert actual.get_aux_mode() == AuxMode.STARTER_VOLTAGE
        assert actual.get_current() == 0.0
        assert actual.get_voltage() == 12.52
        assert actual.get_starter_voltage() == -0.01
        assert actual.get_alarm() == None
        assert actual.get_temperature() == None

    def test_aux_starter(self) -> None:
        actual = self.parse_decrypted("fdffe4040000ffff00000059a65a1c8c")
        assert actual.get_aux_mode() == AuxMode.STARTER_VOLTAGE
        assert actual.get_starter_voltage() == -0.01

    def test_aux_temperature_none(self) -> None:
        actual = self.parse_decrypted("fdffe4040000ffff020000ae28af8a5c")
        assert actual.get_aux_mode() == AuxMode.TEMPERATURE
        assert actual.get_temperature() is None

    def test_aux_temperature(self) -> None:
        actual = self.parse_decrypted("fdffe40400008888020000ae28af8a5c")
        assert actual.get_aux_mode() == AuxMode.TEMPERATURE
        assert actual.get_temperature() == 76.37

    def test_generic_source(self) -> None:
        actual = self.parse_decrypted("ffff6f0a0000000003000043698118eb")
        assert actual.get_meter_type() == MeterType.GENERIC_SOURCE
        assert actual.get_aux_mode() == AuxMode.DISABLED
        assert actual.get_current() == 0.0
        assert actual.get_voltage() == 26.71
        assert actual.get_starter_voltage() is None
        assert actual.get_alarm() is None
        assert actual.get_temperature() is None
