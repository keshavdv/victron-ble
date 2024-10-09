from victron_ble.devices.base import ACInState, AlarmNotification, OperationMode
from victron_ble.devices.vebus import VEBus


class TestVEBus:
    def test_parse_data(self) -> None:
        data = "100380270c1252dad26f0b8eb39162074d140df410"
        actual = VEBus("da3f5fa2860cb1cf86ba7a6d1d16b9dd").parse(bytes.fromhex(data))

        assert actual.get_device_state() == OperationMode.FLOAT
        assert actual.get_error() == 0
        assert actual.get_alarm() == AlarmNotification.NO_ALARM
        assert actual.get_battery_voltage() == 14.45
        assert actual.get_battery_current() == 23.2
        assert actual.get_ac_in_state() == ACInState.AC_IN_1
        assert actual.get_ac_in_power() == 1459
        assert actual.get_ac_out_power() == 1046
        assert actual.get_battery_temperature() == 32
        assert actual.get_soc() == None

    def test_inverter(self) -> None:
        data = "100380270ce1b2dabd34912a6ecec963899227a220"
        actual = VEBus("da3f5fa2860cb1cf86ba7a6d1d16b9dd").parse(bytes.fromhex(data))

        assert actual.get_device_state() == OperationMode.INVERTING
        assert actual.get_error() == 0
        assert actual.get_alarm() == AlarmNotification.NO_ALARM
        assert actual.get_battery_voltage() == 12.43
        assert actual.get_battery_current() == -5.9
        assert actual.get_ac_in_state() == ACInState.NOT_CONNECTED
        assert actual.get_ac_in_power() == 0
        assert actual.get_ac_out_power() == 45
        assert actual.get_battery_temperature() == 30
        assert actual.get_soc() == None

    def test_off(self) -> None:
        data = "100380270c65b8dad9dd594c7f57d1de9e27a3e2ab"
        actual = VEBus("da3f5fa2860cb1cf86ba7a6d1d16b9dd").parse(bytes.fromhex(data))

        assert actual.get_device_state() == OperationMode.OFF
        assert actual.get_error() == 0
        assert actual.get_alarm() == AlarmNotification.NO_ALARM
        assert actual.get_model_name() == "Victron Multiplus II 12/3000/120-50 2x120V"
