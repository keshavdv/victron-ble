from victron_ble.devices.base import OperationMode
from victron_ble.devices.solar_charger import SolarCharger, SolarChargerData


class TestSolarCharger:
    def test_end_to_end_parse(self) -> None:
        data = "100242a0016207adceb37b605d7e0ee21b24df5c"
        actual = SolarCharger("adeccb947395801a4dd45a2eaa44bf17").parse(
            bytes.fromhex(data)
        )

        assert isinstance(actual, SolarChargerData)
        assert actual.get_charge_state() == OperationMode.ABSORPTION
        assert actual.get_battery_voltage() == 13.88
        assert actual.get_battery_charging_current() == 1.4
        assert actual.get_yield_today() == 30
        assert actual.get_solar_power() == 19
        assert actual.get_external_device_load() == 0.0
        assert actual.get_model_name() == "BlueSolar MPPT 75|15"

    def parse_decrypted(self, decrypted: str) -> SolarChargerData:
        parsed = SolarCharger(None).parse_decrypted(bytes.fromhex(decrypted))
        return SolarChargerData(None, parsed)

    def test_parse(self) -> None:
        actual = self.parse_decrypted("04006c050e000300130000fe409ac069")
        assert actual.get_charge_state() == OperationMode.ABSORPTION
        assert actual.get_battery_voltage() == 13.88
        assert actual.get_battery_charging_current() == 1.4
        assert actual.get_yield_today() == 30
        assert actual.get_solar_power() == 19
        assert actual.get_external_device_load() == 0.0

    def test_bulk_charge(self) -> None:
        actual = self.parse_decrypted("0300f80402000200030000fe8c9a5572")
        assert actual.get_charge_state() == OperationMode.BULK

    def test_parse_mppt100(self) -> None:
        actual = self.parse_decrypted("0300fb09650032000901ffff31bc45ad")
        assert actual.get_battery_charging_current() == 10.1
        assert actual.get_battery_voltage() == 25.55
        assert actual.get_charge_state() == OperationMode.BULK
        assert actual.get_solar_power() == 265
        assert actual.get_yield_today() == 500
        assert actual.get_external_device_load() is None
