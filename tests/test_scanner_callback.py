import json
from unittest.mock import patch
from victron_ble.scanner import Scanner

class DummyDevice:
    def __init__(self, address="AA:BB:CC:DD:EE:FF", name="TestDevice"):
        self.address = address
        self.name = name

class DummyDeviceType:
    def __init__(self, key):
        self.key = key
    def parse(self, raw_data):
        return {"parsed": True}

def test_callback_with_none_rssi(monkeypatch):
    scanner = Scanner(device_keys={"aa:bb:cc:dd:ee:ff": "dummykey"})
    device = DummyDevice()
    raw_data = b"\x10\x01\x02"
    monkeypatch.setattr("victron_ble.scanner.detect_device_type", lambda data: DummyDeviceType)
    monkeypatch.setattr("victron_ble.scanner.DeviceDataEncoder", lambda *a, **kw: json.JSONEncoder())
    with patch("builtins.print") as mock_print:
        scanner.callback(device, raw_data, rssi=None)
        mock_print.assert_called()
        args, kwargs = mock_print.call_args
        assert '"rssi": null' in args[0]

def test_callback_with_omitted_rssi(monkeypatch):
    scanner = Scanner(device_keys={"aa:bb:cc:dd:ee:ff": "dummykey"})
    device = DummyDevice()
    raw_data = b"\x10\x01\x02"
    monkeypatch.setattr("victron_ble.scanner.detect_device_type", lambda data: DummyDeviceType)
    monkeypatch.setattr("victron_ble.scanner.DeviceDataEncoder", lambda *a, **kw: json.JSONEncoder())
    with patch("builtins.print") as mock_print:
        scanner.callback(device, raw_data)
        mock_print.assert_called()
        args, kwargs = mock_print.call_args
        assert '"rssi": null' in args[0]

def test_callback_with_int_rssi(monkeypatch):
    scanner = Scanner(device_keys={"aa:bb:cc:dd:ee:ff": "dummykey"})
    device = DummyDevice()
    raw_data = b"\x10\x01\x02"
    monkeypatch.setattr("victron_ble.scanner.detect_device_type", lambda data: DummyDeviceType)
    monkeypatch.setattr("victron_ble.scanner.DeviceDataEncoder", lambda *a, **kw: json.JSONEncoder())
    with patch("builtins.print") as mock_print:
        scanner.callback(device, raw_data, rssi=-55)
        mock_print.assert_called()
        args, kwargs = mock_print.call_args
        assert '"rssi": -55' in args[0]


