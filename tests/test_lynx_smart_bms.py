from victron_ble.devices.lynx_smart_bms import LynxSmartBMS, LynxSmartBMSData


class TestLynxSmartBMS:
    def parse_decrypted(self, decrypted: bytes) -> LynxSmartBMSData:
        parsed = LynxSmartBMS(None).parse_decrypted(decrypted)
        return LynxSmartBMSData(None, parsed)

    def test_parse(self) -> None:
        actual = self.parse_decrypted(
            b"\x00@8\x8b\n\xfa\xff\x95\x15U\x14\x8c\xcf\x02\x00\xff\xb3\xea\xf1t\xd6\xfczHT\xb8\xec\x00\x86\t\xe9\xca"
        )
        assert actual.get_battery_temperature() is None
        assert actual.get_consumed_ah() == 4.4
        assert actual.get_soc() == 99.5
        assert actual.get_alarm_flags() == 5205  # ??
        assert actual.get_io_status() == 5525  # ??
        assert actual.get_current() == -0.6
        assert actual.get_voltage() == 26.99
        assert actual.get_remaining_mins() == 14400
        assert actual.get_error_flags() == 0
