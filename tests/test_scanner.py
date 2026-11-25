import json
from unittest.mock import Mock

import pytest
from bleak.backends.device import BLEDevice
from bleak.backends.scanner import AdvertisementData

from victron_ble.scanner import Scanner

# Existing encrypted SolarCharger fixture and its test key.
ADVERTISEMENT = bytes.fromhex("100242a0016207adceb37b605d7e0ee21b24df5c")
KEY = "adeccb947395801a4dd45a2eaa44bf17"


@pytest.mark.parametrize(
    "configured,discovered",
    [
        ("d8ab020cfea4", "D8:AB:02:0C:FE:A4"),
        ("D8AB020CFEA4", "d8:ab:02:0c:fe:a4"),
        ("D8:AB:02:0C:FE:A4", "d8:ab:02:0c:fe:a4"),
        ("d8:ab:02:0c:fe:a4", "D8AB020CFEA4"),
        (
            "F20DC488-1A9C-45A0-AB12-AABBCCDDEEFF",
            "f20dc488-1a9c-45a0-ab12-aabbccddeeff",
        ),
    ],
)
def test_read_advertisement_with_address_formats(
    monkeypatch, capsys, configured, discovered
):
    # Only replace the radio scanner: dispatch, device detection, decryption and
    # printed measurements use the production implementation.
    monkeypatch.setattr("victron_ble.scanner.BleakScanner", Mock())
    scanner = Scanner({configured: KEY})
    device = BLEDevice(discovered, "Solar charger", {})
    advertisement = AdvertisementData(
        local_name="Solar charger",
        manufacturer_data={0x02E1: ADVERTISEMENT},
        service_data={},
        service_uuids=[],
        tx_power=None,
        rssi=-63,
        platform_data=(),
    )
    scanner._detection_callback(device, advertisement)
    result = json.loads(capsys.readouterr().out)
    assert result["address"] == discovered
    assert result["rssi"] == -63
    assert result["payload"]["battery_voltage"] == 13.88
    assert result["payload"]["solar_power"] == 19


def test_unconfigured_device_is_still_ignored(monkeypatch, capsys):
    monkeypatch.setattr("victron_ble.scanner.BleakScanner", Mock())
    scanner = Scanner({"d8ab020cfea4": KEY})
    device = BLEDevice("D8:AB:02:0C:FE:A5", "Other charger", {})
    advertisement = AdvertisementData(
        local_name="Other charger",
        manufacturer_data={0x02E1: ADVERTISEMENT},
        service_data={},
        service_uuids=[],
        tx_power=None,
        rssi=-63,
        platform_data=(),
    )
    scanner._detection_callback(device, advertisement)
    assert capsys.readouterr().out == ""
