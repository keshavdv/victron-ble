from victron_ble.devices import detect_device_type, BatteryMonitor, Device


def test_unknown_device_type():
    assert detect_device_type(bytes.fromhex("10020000")) == None


def test_battery_monitor_discovery():
    assert detect_device_type(bytes.fromhex("100289a3")) == BatteryMonitor
