from victron_ble.devices.smart_lithium import (
    BalancerStatus,
    SmartLithium,
    SmartLithiumData,
)


class TestSmartLithium:
    def parse_decrypted(self, decrypted: bytes) -> SmartLithiumData:
        parsed = SmartLithium(None).parse_decrypted(decrypted)
        return SmartLithiumData(None, parsed)

    def test_parse(self) -> None:
        actual = self.parse_decrypted(
            b"\x00\x00\x00\x06\x00\x00\xc7\xe3\xf1\xf8\xff\xff\xff,5\xb5\xfa\xb4x\x01\x0f\xd2I\xd2\xae_iV\xe1\xf8\xa9e"
        )
        assert actual.get_error_flags() == 0
        assert actual.get_balancer_status() == BalancerStatus.IMBALANCE
        assert actual.get_battery_temperature() == 13
        assert actual.get_battery_voltage() == 13.24
        assert actual.get_bms_flags() == 100663296
        assert actual.get_cell_voltages() == [
            3.31,
            3.31,
            3.31,
            3.31,
            None,
            None,
            None,
            None,
        ]

    def test_parse_2(self) -> None:
        actual = self.parse_decrypted(
            b"\x00\x00\x00\x06\x00\x00\xc7\xe3\xf1\xf8\xff\xff\xff,\x15\xb6\x84\x9a\xea \x97}\x8c\xa2\xb6\xf92\xde\x82\x8a\x88\xf9"
        )
        assert actual.get_balancer_status() == BalancerStatus.BALANCED
        assert actual.get_battery_temperature() == 14
        assert actual.get_battery_voltage() == 13.24
        assert actual.get_bms_flags() == 100663296
        assert actual.get_cell_voltages() == [
            3.31,
            3.31,
            3.31,
            3.31,
            None,
            None,
            None,
            None,
        ]
        assert actual.get_error_flags() == 0

    def test_parse_3(self) -> None:
        actual = self.parse_decrypted(
            b"\x00\x00\x00\x06\x00\x00\xc7\xe3\xd1\xf8\xff\xff\xff+5\xb5[\xe5\x93\xfd93\xe4\x1c?C\xcefA\xe7q\xa3"
        )
        assert actual.get_balancer_status() == BalancerStatus.IMBALANCE
        assert actual.get_battery_temperature() == 13
        assert actual.get_battery_voltage() == 13.23
        assert actual.get_bms_flags() == 100663296
        assert actual.get_cell_voltages() == [
            3.31,
            3.31,
            3.31,
            3.3,
            None,
            None,
            None,
            None,
        ]
        assert actual.get_error_flags() == 0

    def test_parse_4(self) -> None:
        actual = self.parse_decrypted(
            b"\x00\x00\x00\x06\x00\x00G\xa3\xd1h,\x1a\x8dP\n\xcd\x96d\xf2\xf5\x0b\x85\xed\xe8h\xf6\x1d\xc1\xae\xa1\xce\x83"
        )
        assert actual.get_balancer_status() == BalancerStatus.UNKNOWN
        assert actual.get_battery_temperature() == 37
        assert actual.get_battery_voltage() == 26.4
        assert actual.get_bms_flags() == 100663296  # ?
        assert actual.get_cell_voltages() == [
            3.31,
            3.30,
            3.30,
            3.30,
            3.30,
            3.29,
            3.30,
            3.30,
        ]

    def test_parse_5(self) -> None:
        actual = self.parse_decrypted(
            b"\x00\x00\x00\x06\x00\x00\xcc\xe5\x92\xb9\\.\x99{\x1a\xd0P%\xcf\xa5\xa6\xb2[\x91<T\x85\xee\x85by\xae"
        )
        assert actual.get_balancer_status() == BalancerStatus.BALANCED
        assert actual.get_battery_temperature() == 40
        assert actual.get_battery_voltage() == 26.83
        assert actual.get_bms_flags() == 100663296  # ?
        assert actual.get_cell_voltages() == [
            3.36,
            3.35,
            3.35,
            3.36,
            3.35,
            3.35,
            3.35,
            3.36,
        ]
