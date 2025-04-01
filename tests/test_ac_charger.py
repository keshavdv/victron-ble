from victron_ble.devices.base import OperationMode, ChargerError
from victron_ble.devices.ac_charger import AcCharger, AcChargerData


class TestAcCharger:
    def test_end_to_end_parse(self) -> None:
        data = "100030a308f926c1b5170a0d2280335bf12d5ed083"
        actual = AcCharger("c129cf8f75c3fe5a1655b481e205fb7d").parse(
            bytes.fromhex(data)
        )

        assert isinstance(actual, AcChargerData)
        assert actual.get_charge_state() == OperationMode.STORAGE
        assert actual.get_charger_error() == ChargerError.NO_ERROR
        assert actual.get_output_voltage1() == 13.49
        assert actual.get_output_current1() == 0.4
        assert actual.get_ac_current() == None
        assert actual.get_output_current2() == None
        assert actual.get_model_name() == "Blue Smart IP22 Charger 12/30"

    def parse_decrypted(self, decrypted: str) -> AcChargerData:
        parsed = AcCharger(None).parse_decrypted(bytes.fromhex(decrypted))
        return AcChargerData(None, parsed)

    def test_parse(self) -> None:
        actual = self.parse_decrypted("060046a500ffffffffffffbdffeb3d1f")
        assert actual.get_charge_state() == OperationMode.STORAGE
        assert actual.get_charger_error() == ChargerError.NO_ERROR
        assert actual.get_output_voltage1() == 13.5
        assert actual.get_output_current1() == 0.5
        assert actual.get_output_current2() == None
