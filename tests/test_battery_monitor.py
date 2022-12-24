from victron_ble.devices import BatteryMonitor


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
            "aux": 0,
            "aux_mode": 3,
            "consumed_ah": 50.0,
            "current": 0,
            "remaining_mins": 65535,
            "soc": 50.0,
            "voltage": 12.53,
        }

        key = "aff4d0995b7d1e176c0c33ecb9e70dcd"
        data = "100289a302b040af925d09a4d89aa0128bdef48c6298a9"
        actual = BatteryMonitor(key).parse(bytes.fromhex(data))
        assert actual == expected
