from victron_ble.devices.base import BitReader, OffReason


class TestOffReason:
    def test_known_values(self) -> None:
        """Known OffReason values should resolve to the expected enum members."""
        assert OffReason.NO_REASON == OffReason(0x00000000)
        assert OffReason.ENGINE_SHUTDOWN == OffReason(0x00000080)
        assert (
            OffReason.ENGINE_SHUTDOWN_AND_INPUT_VOLTAGE_LOCKOUT
            == OffReason(0x00000081)
        )

    def test_unknown_value_creates_synthetic_member(self) -> None:
        """Unknown values should produce a synthetic member instead of crashing."""
        member = OffReason(137)
        assert member.name == "UNKNOWN_137"
        assert member.value == 137

    def test_unknown_value_preserves_raw_value(self) -> None:
        """The raw integer value should be preserved in the synthetic member."""
        member = OffReason(999)
        assert member.value == 999
        assert member.name == "UNKNOWN_999"


class TestBitReader:
    def test_to_signed_int(self) -> None:
        assert BitReader.to_signed_int(0x000, 12) == 0x000
        assert BitReader.to_signed_int(0x001, 12) == 0x001
        assert BitReader.to_signed_int(0x242, 12) == 0x242
        assert BitReader.to_signed_int(0x7FF, 12) == 0x7FF
        assert BitReader.to_signed_int(0x800, 12) == -0x800
        assert BitReader.to_signed_int(0xCAD, 12) == -0x353
        assert BitReader.to_signed_int(0xFFF, 12) == -0x001

        assert BitReader.to_signed_int(0x00, 5) == 0x00
        assert BitReader.to_signed_int(0x01, 5) == 0x01
        assert BitReader.to_signed_int(0x0F, 5) == 0x0F
        assert BitReader.to_signed_int(0x10, 5) == -0x10
        assert BitReader.to_signed_int(0x1F, 5) == -0x01

    def test_read(self) -> None:
        data = "1a2b3c4d5e6f7890"
        reader = BitReader(bytes.fromhex(data))

        assert reader.read_bit() == 0
        assert reader.read_bit() == 1
        assert reader.read_bit() == 0
        assert reader.read_bit() == 1
        assert reader.read_unsigned_int(6) == 0x31
        assert reader.read_signed_int(6) == 0x0A
        assert reader.read_signed_int(4) == -0x04
        assert reader.read_unsigned_int(11) == 0x4D3
        assert reader.read_bit() == 0
        assert reader.read_unsigned_int(32) == 0x90786F5E
