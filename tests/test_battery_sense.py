from victron_ble.devices import BatterySense


class TestBatterySense:
    def test_parse_data(self) -> None:
        key = "0da694539597f9cf6c613cde60d7bf05"
        data = "1000a4a3025f150d8dcbff517f30eb65e76b22a04ac4e1"
        actual = BatterySense(key).parse(bytes.fromhex(data))
        assert actual.get_temperature() == 22.5
        assert actual.get_voltage() == 12.22
        assert actual.get_model_name() == "Smart Battery Sense"

    def test_parse_data_new_model(self) -> None:
        key = "fee810239c3f4fb775703a4666569569"
        data = "1000a5a3025a0dfec57db3d1493c0b132132210f70475b"
        actual = BatterySense(key).parse(bytes.fromhex(data))
        assert actual.get_temperature() == 17.5
        assert actual.get_voltage() == 12.72
        assert actual.get_model_name() == "Smart Battery Sense"
