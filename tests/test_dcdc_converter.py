from victron_ble.devices.dcdc_converter import DcDcConverter
from victron_ble.devices.base import OperationMode, OffReason, ChargerError


class TestDcDcConverter:
    def test_parse_data(self) -> None:
        data = "1000c0a304121d64ca8d442b90bbdf6a8cba"
        actual = DcDcConverter("64ba49f1a8562e45197a8e1fe50d7658").parse(
            bytes.fromhex(data)
        )

        assert actual.get_charge_state() == OperationMode.OFF
        assert actual.get_charger_error() == ChargerError.NO_ERROR
        assert actual.get_input_voltage() == 13.15
        assert actual.get_output_voltage() == 0
        assert actual.get_off_reason() == OffReason.ENGINE_SHUTDOWN
        assert (
            actual.get_model_name() == "Orion Smart 12V|12V-18A Isolated DC-DC Charger"
        )
