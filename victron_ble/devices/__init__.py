import struct
from typing import Dict, Optional, Type

from victron_ble.devices.base import Device, DeviceData
from victron_ble.devices.battery_monitor import (
    AuxMode,
    BatteryMonitor,
    BatteryMonitorData,
)
from victron_ble.devices.battery_sense import BatterySense, BatterySenseData
from victron_ble.devices.dc_energy_meter import DcEnergyMeter, DcEnergyMeterData
from victron_ble.devices.dcdc_converter import DcDcConverter, DcDcConverterData
from victron_ble.devices.inverter import Inverter, InverterData
from victron_ble.devices.lynx_smart_bms import LynxSmartBMS, LynxSmartBMSData
from victron_ble.devices.orion_xs import OrionXS, OrionXSData
from victron_ble.devices.smart_battery_protect import (
    SmartBatteryProtect,
    SmartBatteryProtectData,
)
from victron_ble.devices.smart_lithium import SmartLithium, SmartLithiumData
from victron_ble.devices.solar_charger import SolarCharger, SolarChargerData
from victron_ble.devices.vebus import VEBus, VEBusData

__all__ = [
    "AuxMode",
    "Device",
    "DeviceData",
    "BatteryMonitor",
    "BatteryMonitorData",
    "BatterySense",
    "BatterySenseData",
    "DcDcConverter",
    "DcDcConverterData",
    "DcEnergyMeter",
    "DcEnergyMeterData",
    "Inverter",
    "InverterData",
    "OrionXS",
    "OrionXSData",
    "SmartBatteryProtect",
    "SmartBatteryProtectData",
    "SmartLithium",
    "SmartLithiumData",
    "SmartBatteryProtect",
    "SmartBatteryProtectData",
    "LynxSmartBMS",
    "LynxSmartBMSData",
    "SolarCharger",
    "SolarChargerData",
    "VEBus",
    "VEBusData",
]

# Add to this list if a device should be forced to use a particular implementation
# instead of relying on the identifier in the advertisement
MODEL_PARSER_OVERRIDE: Dict[int, Type[Device]] = {
    0xA3A4: BatterySense,  # Smart Battery Sense
    0xA3A5: BatterySense,  # Smart Battery Sense
}


def detect_device_type(data: bytes) -> Optional[Type[Device]]:
    try:
        model_id = struct.unpack("<H", data[2:4])[0]
        mode = struct.unpack("<B", data[4:5])[0]
    except IndexError:
        return None

    # Model ID-based preferences
    match = MODEL_PARSER_OVERRIDE.get(model_id)
    if match:
        return match

    # Defaults
    if mode == 0x2:  # BatteryMonitor
        return BatteryMonitor
    elif mode == 0xD:  # DcEnergyMeter
        return DcEnergyMeter
    elif mode == 0x8:  # AcCharger
        pass
    elif mode == 0x4:  # DcDcConverter
        return DcDcConverter
    elif mode == 0x3:  # Inverter
        return Inverter
    elif mode == 0x6:  # InverterRS
        pass
    elif mode == 0xA:  # LynxSmartBMS
        return LynxSmartBMS
    elif mode == 0xB:  # MultiRS
        pass
    elif (
        mode == 0x5
    ):  # SmartLithium (commercially Lithium Battery Smart / LiFePO4 Battery Smart)
        return SmartLithium
    elif mode == 0x9:  # SmartBatteryProtect
        return SmartBatteryProtect
    elif mode == 0x1:  # SolarCharger
        return SolarCharger
    elif mode == 0xC:  # VE.Bus
        return VEBus
    elif mode == 0xF:  # Orion XS
        return OrionXS

    return None
