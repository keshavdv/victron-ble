from victron_ble.devices.battery_monitor import BatteryMonitor, AuxMode


class TestBatteryMonitor:
    def test_parse_data(self) -> None:
        data = "100289a302b040af925d09a4d89aa0128bdef48c6298a9"
        actual = BatteryMonitor("aff4d0995b7d1e176c0c33ecb9e70dcd").parse(
            bytes.fromhex(data)
        )
        assert actual.get_aux_mode() == AuxMode.DISABLED
        assert actual.get_consumed_ah() == 50.0
        assert actual.get_current() == 0
        assert actual.get_remaining_mins() == 65535
        assert actual.get_soc() == 50.0
        assert actual.get_voltage() == 12.53
        assert actual.get_high_starter_battery_voltage_alarm() == False
        assert actual.get_high_temperature_alarm() == False
        assert actual.get_high_voltage_alarm() == False
        assert actual.get_low_soc_alarm() == False
        assert actual.get_low_starter_battery_voltage_alarm() == False
        assert actual.get_low_temperature_alarm() == False
        assert actual.get_low_voltage_alarm() == False
        assert actual.get_midpoint_deviation_alarm() == False

        assert actual.get_temperature() == None
        assert actual.get_starter_voltage() == None
        assert actual.get_midpoint_voltage() == None

    def test_aux_midpoint(self) -> None:
        data = "100289a3021001afc15f433b2663c8cfc0678b5d3d29a8"
        actual = BatteryMonitor("aff4d0995b7d1e176c0c33ecb9e70dcd").parse(
            bytes.fromhex(data)
        )
        assert actual.get_midpoint_voltage() == 655.34

    def test_aux_starter(self) -> None:
        data = "100289a302c802af45fc59d010dd78d2948e0c55c3bf48"
        actual = BatteryMonitor("aff4d0995b7d1e176c0c33ecb9e70dcd").parse(
            bytes.fromhex(data)
        )
        assert actual.get_starter_voltage() == -0.02

    def test_aux_temperature(self) -> None:
        data = "100289a302bb01af129087600b9b97bc2c32867c8238da"
        actual = BatteryMonitor("aff4d0995b7d1e176c0c33ecb9e70dcd").parse(
            bytes.fromhex(data)
        )
        assert actual.get_temperature() == 382.2
