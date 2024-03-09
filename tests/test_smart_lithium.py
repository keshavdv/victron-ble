import pytest

from victron_ble.devices.smart_lithium import SmartLithium, SmartLithiumData


class TestSmartLithium:
    def parse_decrypted(self, decrypted: bytes) -> SmartLithiumData:
        parsed = SmartLithium(None).parse_decrypted(decrypted)
        return SmartLithiumData(None, parsed)

    def test_parse(self) -> None:
        actual = self.parse_decrypted(
            b"\x00\x00\x00\x06\x00\x00\xc7\xe3\xf1\xf8\xff\xff\xff,5\xb5\xfa\xb4x\x01\x0f\xd2I\xd2\xae_iV\xe1\xf8\xa9e"
        )
        assert actual.get_balancer_status() == 5
        assert actual.get_battery_temperature() == 50  # TODO this should be around 10C
        assert actual.get_battery_voltage() == 7.07  # TODO this should be >13
        assert actual.get_bms_flags() == 6
        assert actual.get_cell_voltages() == [
            3.59,
            3.8,
            float("inf"),
            2.91,
            3.31,
            None,
            None,
            None,
        ]
        assert actual.get_error_flags() == 0

    def test_parse_2(self) -> None:
        actual = self.parse_decrypted(
            b"\x00\x00\x00\x06\x00\x00\xc7\xe3\xf1\xf8\xff\xff\xff,\x15\xb6\x84\x9a\xea \x97}\x8c\xa2\xb6\xf92\xde\x82\x8a\x88\xf9"
        )
        assert actual.get_balancer_status() == 5
        assert actual.get_battery_temperature() == 51  # TODO this should be around 10C
        assert actual.get_battery_voltage() == 7.05  # TODO this should be >13
        assert actual.get_bms_flags() == 6
        assert actual.get_cell_voltages() == [
            3.59,
            3.8,
            float("inf"),
            2.91,
            3.31,
            None,
            None,
            None,
        ]  # TODO this is random, but for some reason the same as with the other battery...
        assert actual.get_error_flags() == 0

    def test_parse_3(self) -> None:
        actual = self.parse_decrypted(
            b"\x00\x00\x00\x06\x00\x00\xc7\xe3\xd1\xf8\xff\xff\xff+5\xb5[\xe5\x93\xfd93\xe4\x1c?C\xcefA\xe7q\xa3"
        )
        assert actual.get_balancer_status() == 5
        assert actual.get_battery_temperature() == 50  # TODO this should be around 10C
        assert actual.get_battery_voltage() == 6.91  # TODO this should be >13
        assert actual.get_bms_flags() == 6
        assert actual.get_cell_voltages() == [
            3.59,
            3.8,
            3.8200000000000003,
            2.91,
            3.31,
            None,
            None,
            None,
        ]  # TODO this is random, but for some reason ALMOST the same as with the other battery...
        assert actual.get_error_flags() == 0
