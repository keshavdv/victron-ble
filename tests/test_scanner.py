from unittest.mock import MagicMock, patch

import pytest

from victron_ble.exceptions import AdvertisementKeyMissingError


def make_scanner(device_keys):
    with patch("victron_ble.scanner.BleakScanner"):
        from victron_ble.scanner import Scanner

        return Scanner(device_keys)


def make_ble_device(address: str):
    device = MagicMock()
    device.address = address
    return device


class TestScannerMacNormalization:
    """Tests that MAC addresses are normalized (colons stripped) for key lookup."""

    def test_key_stored_with_colons_matches_address_without_colons(self):
        scanner = make_scanner({"d8:ab:02:0c:fe:a4": "aabbccddeeff00112233445566778899"})
        assert scanner.load_key("d8ab020cfea4") == "aabbccddeeff00112233445566778899"

    def test_key_stored_without_colons_matches_address_without_colons(self):
        scanner = make_scanner({"d8ab020cfea4": "aabbccddeeff00112233445566778899"})
        assert scanner.load_key("d8ab020cfea4") == "aabbccddeeff00112233445566778899"

    def test_get_device_normalizes_ble_device_address_with_colons(self):
        key = "aff4d0995b7d1e176c0c33ecb9e70dcd"
        # Store key without colons (as user might provide)
        scanner = make_scanner({"d8ab020cfea4": key})
        # BLE device returns address with colons (as bleak does on Linux)
        ble_device = make_ble_device("D8:AB:02:0C:FE:A4")
        raw_data = bytes.fromhex("100289a302b040af925d09a4d89aa0128bdef48c6298a9")
        device = scanner.get_device(ble_device, raw_data)
        assert device is not None

    def test_get_device_key_with_colons_matches_ble_device_without_colons(self):
        key = "aff4d0995b7d1e176c0c33ecb9e70dcd"
        # Store key with colons (as Victron app provides)
        scanner = make_scanner({"d8:ab:02:0c:fe:a4": key})
        # BLE device returns address without colons
        ble_device = make_ble_device("d8ab020cfea4")
        raw_data = bytes.fromhex("100289a302b040af925d09a4d89aa0128bdef48c6298a9")
        device = scanner.get_device(ble_device, raw_data)
        assert device is not None

    def test_missing_key_still_raises(self):
        scanner = make_scanner({"aabbccddeeff": "aabbccddeeff00112233445566778899"})
        with pytest.raises(AdvertisementKeyMissingError):
            scanner.load_key("d8ab020cfea4")
