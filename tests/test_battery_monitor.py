import pytest

from victron_ble.devices.battery_monitor import (
    AlarmReason,
    AuxMode,
    BatteryMonitor,
    BatteryMonitorData,
)
from victron_ble.exceptions import AdvertisementKeyMismatchError


class TestBatteryMonitor:
    def test_end_to_end_parse(self) -> None:
        data = "100289a302b040af925d09a4d89aa0128bdef48c6298a9"
        actual = BatteryMonitor("aff4d0995b7d1e176c0c33ecb9e70dcd").parse(
            bytes.fromhex(data)
        )
        assert isinstance(actual, BatteryMonitorData)
        assert actual.get_aux_mode() == AuxMode.DISABLED
        assert actual.get_consumed_ah() == -50.0
        assert actual.get_current() == 0
        assert actual.get_remaining_mins() == None
        assert actual.get_soc() == 50.0
        assert actual.get_voltage() == 12.53
        assert actual.get_alarm() == AlarmReason.NO_ALARM
        assert actual.get_temperature() == None
        assert actual.get_starter_voltage() == None
        assert actual.get_midpoint_voltage() == None
        assert actual.get_model_name() == "SmartShunt 500A/50mV"

    def parse_decrypted(self, decrypted: str) -> BatteryMonitorData:
        parsed = BatteryMonitor(None).parse_decrypted(bytes.fromhex(decrypted))
        return BatteryMonitorData(None, parsed)

    def test_parse(self) -> None:
        actual = self.parse_decrypted("ffffe50400000000030000f40140df03")
        assert actual.get_aux_mode() == AuxMode.DISABLED
        assert actual.get_consumed_ah() == -50.0
        assert actual.get_current() == 0
        assert actual.get_remaining_mins() == None
        assert actual.get_soc() == 50.0
        assert actual.get_voltage() == 12.53
        assert actual.get_alarm() == AlarmReason.NO_ALARM
        assert actual.get_temperature() == None
        assert actual.get_starter_voltage() == None
        assert actual.get_midpoint_voltage() == None

    def test_aux_midpoint(self) -> None:
        actual = self.parse_decrypted("ffffe6040000feff010000000080fe0c")
        assert actual.get_midpoint_voltage() == 655.34

    def test_aux_starter(self) -> None:
        actual = self.parse_decrypted("ffffe6040000feff000000000080feac")
        assert actual.get_starter_voltage() == -0.02

    def test_aux_temperature(self) -> None:
        actual = self.parse_decrypted("ffffe6040000ffff020000000080fede")
        assert actual.get_temperature() == 382.2

    def test_key_mismatch(self) -> None:
        data = "100289a302bb01af129087600b9b97bc2c32867c8238da"
        with pytest.raises(AdvertisementKeyMismatchError):
            BatteryMonitor("ffffffffffffffffffffffffffffffff").parse(
                bytes.fromhex(data)
            )
