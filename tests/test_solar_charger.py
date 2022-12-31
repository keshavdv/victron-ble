from victron_ble.devices.solar_charger import SolarCharger
from victron_ble.devices.base import OperationMode


class TestSolarChargwer:
    def test_parse_data(self) -> None:
        data = "100242a0016207adceb37b605d7e0ee21b24df5c"
        actual = SolarCharger("adeccb947395801a4dd45a2eaa44bf17").parse(
            bytes.fromhex(data)
        )

        assert actual.get_charge_state() == OperationMode.ABSORPTION
        assert actual.get_battery_voltage() == 13.88
        assert actual.get_battery_charging_current() == 1.4
        assert actual.get_yield_today() == 30
        assert actual.get_solar_power() == 19
        assert actual.get_external_device_load() == 0.0

    def test_bulk_charge(self) -> None:
        data = "100242a0015939a26cc2941a491e766be8457386"
        actual = SolarCharger("a2781bef23aecd48d6b9397350724c67").parse(
            bytes.fromhex(data)
        )
        assert actual.get_charge_state() == OperationMode.BULK
