import pytest

from victron_ble.devices import SolarSense, SolarSenseData, detect_device_type


def _advertisement() -> bytes:
    fields = (
        (32, 0),
        (8, 0xFF),
        (20, 180),
        (20, 123),
        (14, 8500),
        (11, 800),
        (1, 0),
        (8, 210),
        (1, 0),
        (7, 10),
    )
    payload = bytearray(16)
    bit_offset = 0
    for bit_count, value in fields:
        for bit in range(bit_count):
            payload[(bit_offset + bit) // 8] |= (value >> bit & 1) << (
                (bit_offset + bit) % 8
            )
        bit_offset += bit_count
    return bytes.fromhex("100250c001000001") + payload


def test_solar_sense_discovery() -> None:
    assert detect_device_type(_advertisement()) is SolarSense


def test_plaintext_advertisement_parse() -> None:
    actual = SolarSense("").parse(_advertisement())

    assert isinstance(actual, SolarSenseData)
    assert actual.get_installation_power() == 180
    assert actual.get_yield_today() == 1230
    assert actual.get_irradiance() == 850
    assert actual.get_cell_temperature() == 20
    assert actual.get_model_name() == "SolarSense 750"


def test_unavailable_values() -> None:
    fields = (
        (32, 0),
        (8, 0xFF),
        (20, 0xFFFFF),
        (20, 0xFFFFF),
        (14, 0x3FFF),
        (11, 0x7FF),
        (1, 0),
        (8, 0xFF),
        (1, 0),
        (7, 0x7F),
    )
    payload = bytearray(16)
    bit_offset = 0
    for bit_count, value in fields:
        for bit in range(bit_count):
            payload[(bit_offset + bit) // 8] |= (value >> bit & 1) << (
                (bit_offset + bit) % 8
            )
        bit_offset += bit_count

    actual = SolarSense("").parse(bytes.fromhex("100250c001000001") + payload)

    assert actual.get_installation_power() is None
    assert actual.get_yield_today() is None
    assert actual.get_irradiance() is None
    assert actual.get_cell_temperature() is None


def test_incomplete_advertisement() -> None:
    with pytest.raises(ValueError, match="advertisement is incomplete"):
        SolarSense("").parse(bytes.fromhex("100250c001000000"))
