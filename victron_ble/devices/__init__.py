from construct import Int16ul

from victron_ble.devices.base import Device
from victron_ble.devices.battery_monitor import BatteryMonitor
from victron_ble.devices.smart_battery_sense import SmartBatterySense


__all__ = ["Device", "BatteryMonitor", "SmartBatterySense"]

MODEL_MAPPING = {
    0xA381: BatteryMonitor,     # BMV-712 Smart
    0xA382: BatteryMonitor,     # BMV-710H Smart
    0xA383: BatteryMonitor,     # BMV-712 Smart Rev2
    0xA389: BatteryMonitor,     # SmartShunt 500A/50mV
    0xA38A: BatteryMonitor,     # SmartShunt 1000A/50mV
    0xA38B: BatteryMonitor,     # SmartShunt 2000A/50mV
    0xA3A4: SmartBatterySense,  # Smart Battery Sense
}


def detect_device_type(data):
    model_id = Int16ul.parse(data[2:4])
    return MODEL_MAPPING.get(model_id)
