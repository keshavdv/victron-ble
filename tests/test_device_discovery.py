from victron_ble.devices import (
    BatteryMonitor,
    BatterySense,
    DcEnergyMeter,
    detect_device_type,
)


def test_unknown_device_type() -> None:
    assert detect_device_type(bytes.fromhex("1002000000")) == None


def test_battery_monitor_discovery() -> None:
    assert detect_device_type(bytes.fromhex("100289a302")) == BatteryMonitor


def test_dc_energy_discovery() -> None:
    assert detect_device_type(bytes.fromhex("100289a30d")) == DcEnergyMeter


def test_battery_sense_discovery() -> None:
    assert detect_device_type(bytes.fromhex("1002a4a302")) == BatterySense
