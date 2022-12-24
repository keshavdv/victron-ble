from victron_ble.devices.base import kelvin_to_celsius


def test_kelvin_to_celsius() -> None:
    assert kelvin_to_celsius(295.65) == 22.5
