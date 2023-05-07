from victron_ble.devices.battery_sense import BatterySense, BatterySenseData


class TestBatterySense:
    def test_end_to_end_parse(self) -> None:
        key = "0da694539597f9cf6c613cde60d7bf05"
        data = "1000a4a3025f150d8dcbff517f30eb65e76b22a04ac4e1"
        actual = BatterySense(key).parse(bytes.fromhex(data))
        assert isinstance(actual, BatterySenseData)
        assert actual.get_temperature() == 22.5
        assert actual.get_voltage() == 12.22
        assert actual.get_model_name() == "Smart Battery Sense"

    def parse_decrypted(self, decrypted: str) -> BatterySenseData:
        parsed = BatterySense(None).parse_decrypted(bytes.fromhex(decrypted))
        return BatterySenseData(None, parsed)

    def test_parse(self) -> None:
        actual = self.parse_decrypted("ffffc60400007d73feff7fffffffff12")
        assert actual.get_temperature() == 22.5
        assert actual.get_voltage() == 12.22

    def test_parse_data_new_model(self) -> None:
        actual = self.parse_decrypted("fffff80400008971feff7fffffffff5c")
        assert actual.get_temperature() == 17.5
        assert actual.get_voltage() == 12.72
