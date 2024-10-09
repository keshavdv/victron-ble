from victron_ble.devices.base import ChargerError, OffReason, OperationMode
from victron_ble.devices.dcdc_converter import DcDcConverter, DcDcConverterData


class TestDcDcConverter:
    def test_end_to_end_parse(self) -> None:
        data = "1000c0a304121d64ca8d442b90bbdf6a8cba"
        actual = DcDcConverter("64ba49f1a8562e45197a8e1fe50d7658").parse(
            bytes.fromhex(data)
        )
        assert isinstance(actual, DcDcConverterData)

        assert actual.get_charge_state() == OperationMode.OFF
        assert actual.get_charger_error() == ChargerError.NO_ERROR
        assert actual.get_input_voltage() == 13.15
        assert actual.get_output_voltage() == None
        assert actual.get_off_reason() == OffReason.ENGINE_SHUTDOWN
        assert (
            actual.get_model_name() == "Orion Smart 12V|12V-18A Isolated DC-DC Charger"
        )

    def parse_decrypted(self, decrypted: str) -> DcDcConverterData:
        parsed = DcDcConverter(None).parse_decrypted(bytes.fromhex(decrypted))
        return DcDcConverterData(None, parsed)

    def test_parse(self) -> None:
        actual = self.parse_decrypted("00002305ff7f80000000cbdd494cc5d1")
        assert actual.get_charge_state() == OperationMode.OFF
        assert actual.get_charger_error() == ChargerError.NO_ERROR
        assert actual.get_input_voltage() == 13.15
        assert actual.get_output_voltage() == None
        assert actual.get_off_reason() == OffReason.ENGINE_SHUTDOWN
