from victron_ble.devices.multirs import MultiRS, MultiRSData, MultiRSOperationMode
from victron_ble.devices.base import ChargerError, ACInState


class TestMultiRS:
    def test_end_to_end_parse(self) -> None:
        """
        Test parsing of a real, encrypted advertisement from a MultiRS device.
        """
        # Sample encrypted advertisement data provided by the user
        data = "100043a40bf4e434af0e46c3b8eb68e08e616993f70c"
        # Correct advertisement key provided by the user
        key = "346c410e8c824dd723c0f5b13b9eabc8"

        actual = MultiRS(key).parse(bytes.fromhex(data))

        assert isinstance(actual, MultiRSData)
        assert actual.get_model_name() == "Multi RS Solar 48V/6000VA/100A"
        assert actual.get_device_state() == MultiRSOperationMode.INVERTING
        assert actual.get_charger_error() == ChargerError.NO_ERROR
        assert actual.get_battery_current() == -12.8
        assert actual.get_battery_voltage() == 51.71
        assert actual.get_active_ac_in() == ACInState.NOT_CONNECTED
        assert actual.get_active_ac_in_power() == 0
        assert actual.get_active_ac_out_power() == 722
        assert actual.get_pv_power() == 0
        assert actual.get_yield_today() == 5.32

    def test_parse(self) -> None:
        """
        Test parsing of a known decrypted payload.
        This is the decrypted version of the payload from test_end_to_end_parse.
        """
        # Decrypted payload: 090080ff33940000d20200001402
        decrypted_payload = "090080ff33940000d20200001402"
        parsed = MultiRS(None).parse_decrypted(bytes.fromhex(decrypted_payload))
        actual = MultiRSData(0xA443, parsed)

        assert actual.get_device_state() == MultiRSOperationMode.INVERTING
        assert actual.get_charger_error() == ChargerError.NO_ERROR
        assert actual.get_battery_current() == -12.8
        assert actual.get_battery_voltage() == 51.71
        assert actual.get_active_ac_in() == ACInState.NOT_CONNECTED
        assert actual.get_active_ac_in_power() == 0
        assert actual.get_active_ac_out_power() == 722
        assert actual.get_pv_power() == 0
        assert actual.get_yield_today() == 5.32

    def test_parse_not_available(self) -> None:
        """
        Test parsing of a payload where some values are marked as "not available".
        """
        # Sample decrypted data where some values are "not available"
        # Byte order for 0x7FFF is ff7f in the string for little-endian parsing
        decrypted_payload = "0900ff7f3294ff7fff7fffff1402"
        parsed = MultiRS(None).parse_decrypted(bytes.fromhex(decrypted_payload))
        actual = MultiRSData(None, parsed)

        assert actual.get_battery_current() is None
        assert actual.get_active_ac_in_power() is None
        assert actual.get_active_ac_out_power() is None
        assert actual.get_pv_power() is None
