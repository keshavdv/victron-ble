from victron_ble.devices import BatteryMonitor, BatterySense


class TestBatteryMonitor:
    def test_parse_data(self):
        expected = {
            "alarm": {
                "high_starter_voltage": False,
                "high_temperature": False,
                "high_voltage": False,
                "low_soc": False,
                "low_starter_voltage": False,
                "low_temperature": False,
                "low_voltage": False,
                "mid_voltage": False,
            },
            "aux_mode": 3,
            "consumed_ah": 50.0,
            "current": 0,
            "remaining_mins": 65535,
            "soc": 50.0,
            "voltage": 12.53,
        }

        data = "100289a302b040af925d09a4d89aa0128bdef48c6298a9"
        actual = BatteryMonitor("aff4d0995b7d1e176c0c33ecb9e70dcd").parse(
            bytes.fromhex(data)
        )
        assert actual == expected

    def test_aux_midpoint(self):
        data = "100289a3021001afc15f433b2663c8cfc0678b5d3d29a8"
        actual = BatteryMonitor("aff4d0995b7d1e176c0c33ecb9e70dcd").parse(
            bytes.fromhex(data)
        )
        assert actual["midpoint_voltage"] == 655.34

    def test_aux_starter(self):
        data = "100289a302c802af45fc59d010dd78d2948e0c55c3bf48"
        actual = BatteryMonitor("aff4d0995b7d1e176c0c33ecb9e70dcd").parse(
            bytes.fromhex(data)
        )
        assert actual["starter_voltage"] == -0.02

    def test_aux_temperature(self):
        data = "100289a302bb01af129087600b9b97bc2c32867c8238da"
        actual = BatteryMonitor("aff4d0995b7d1e176c0c33ecb9e70dcd").parse(
            bytes.fromhex(data)
        )
        assert actual["temperature"] == 65.535


class TestBatterySense:
    def test_parse_data(self):
        expected = {"temperature": 29.565, "voltage": 12.22}

        key = "0da694539597f9cf6c613cde60d7bf05"
        data = "1000a4a3025f150d8dcbff517f30eb65e76b22a04ac4e1"
        actual = BatterySense(key).parse(bytes.fromhex(data))
        assert actual == expected
