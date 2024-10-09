from victron_ble.devices.smart_battery_protect import (
    AlarmReason,
    ChargerError,
    OffReason,
    OperationMode,
    OutputState,
    SmartBatteryProtect,
    SmartBatteryProtectData,
)


class TestSmartBatteryProtect:
    def test_parse(self) -> None:
        data = bytes.fromhex("1080b0a3093523fadedea38b1af8bcbde91ca8b6dbb60e")
        parser = SmartBatteryProtect("fac570d66380b797a5b7543758be00e4").parse(data)
        assert parser.get_alarm_reason() == AlarmReason.NO_ALARM
        assert parser.get_device_state() == OperationMode.ACTIVE
        assert parser.get_error_code() == ChargerError.NO_ERROR
        assert parser.get_input_voltage() == 13.07
        assert parser.get_output_voltage() == 13.07
        assert parser.get_off_reason() == OffReason.NO_REASON
        assert parser.get_output_state() == OutputState.ON
        assert parser.get_warning_reason() == AlarmReason.NO_ALARM
