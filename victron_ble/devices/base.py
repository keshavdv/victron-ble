import abc
import struct
from dataclasses import dataclass
from enum import Enum
from typing import Any, Dict, Type

from Crypto.Cipher import AES
from Crypto.Util import Counter
from Crypto.Util.Padding import pad

from victron_ble.exceptions import AdvertisementKeyMismatchError


# Sourced from VE.Direct docs
class OperationMode(Enum):
    OFF = 0
    LOW_POWER = 1
    FAULT = 2
    BULK = 3
    ABSORPTION = 4
    FLOAT = 5
    STORAGE = 6
    EQUALIZE_MANUAL = 7
    INVERTING = 9
    POWER_SUPPLY = 11
    STARTING_UP = 245
    REPEATED_ABSORPTION = 246
    RECONDITION = 247
    BATTERY_SAFE = 248
    ACTIVE = 249
    EXTERNAL_CONTROL = 252
    NOT_AVAILABLE = 255


# Source: VE.Direct-Protocol-3.32.pdf & https://www.victronenergy.com/live/mppt-error-codes
class ChargerError(Enum):
    # No error
    NO_ERROR = 0
    # Err 1 - Battery temperature too high
    TEMPERATURE_BATTERY_HIGH = 1
    # Err 2 - Battery voltage too high
    VOLTAGE_HIGH = 2
    # Err 3 - Remote temperature sensor failure (auto-reset)
    REMOTE_TEMPERATURE_A = 3
    # Err 4 - Remote temperature sensor failure (auto-reset)
    REMOTE_TEMPERATURE_B = 4
    # Err 5 - Remote temperature sensor failure (not auto-reset)
    REMOTE_TEMPERATURE_C = 5
    # Err 6 - Remote battery voltage sense failure
    REMOTE_BATTERY_A = 6
    # Err 7 - Remote battery voltage sense failure
    REMOTE_BATTERY_B = 7
    # Err 8 - Remote battery voltage sense failure
    REMOTE_BATTERY_C = 8
    # Err 11 - Battery high ripple voltage
    HIGH_RIPPLE = 11
    # Err 14 - Battery temperature too low
    TEMPERATURE_BATTERY_LOW = 14
    # Err 17 - Charger temperature too high
    TEMPERATURE_CHARGER = 17
    # Err 18 - Charger over current
    OVER_CURRENT = 18
    # Err 20 - Bulk time limit exceeded
    BULK_TIME = 20
    # Err 21 - Current sensor issue (sensor bias/sensor broken)
    CURRENT_SENSOR = 21
    # Err 22 - Internal temperature sensor failure
    INTERNAL_TEMPERATURE_A = 22
    # Err 23 - Internal temperature sensor failure
    INTERNAL_TEMPERATURE_B = 23
    # Err 24 - Fan failure
    FAN = 24
    # Err 26 - Terminals overheated
    OVERHEATED = 26
    # Err 27 - Charger short circuit
    SHORT_CIRCUIT = 27
    # Err 28 - Power stage issue Converter issue (dual converter models only)
    CONVERTER_ISSUE = 28
    # Err 29 - Over-Charge protection
    OVER_CHARGE = 29
    # Err 33 - Input voltage too high (solar panel) PV over-voltage
    INPUT_VOLTAGE = 33
    # Err 34 - Input current too high (solar panel) PV over-current
    INPUT_CURRENT = 34
    # Err 35 - PV over-power
    INPUT_POWER = 35
    # Err 38 - Input shutdown (due to excessive battery voltage)
    INPUT_SHUTDOWN_VOLTAGE = 38
    # Err 39 - Input shutdown (due to current flow during off mode)
    INPUT_SHUTDOWN_CURRENT = 39
    # Err 40 - PV Input failed to shutdown
    INPUT_SHUTDOWN_FAILURE = 40
    # Err 41 - Inverter shutdown (PV isolation)
    INVERTER_SHUTDOWN_41 = 41
    # Err 42 - Inverter shutdown (PV isolation)
    INVERTER_SHUTDOWN_42 = 42
    # Err 43 - Inverter shutdown (Ground Fault)
    INVERTER_SHUTDOWN_43 = 43
    # Err 50 - Inverter overload
    INVERTER_OVERLOAD = 50
    # Err 51 - Inverter temperature too high
    INVERTER_TEMPERATURE = 51
    # Err 52 - Inverter peak current
    INVERTER_PEAK_CURRENT = 52
    # Err 53 - Inverter output voltage
    INVERTER_OUPUT_VOLTAGE_A = 53
    # Err 54 - Inverter output voltage
    INVERTER_OUPUT_VOLTAGE_B = 54
    # Err 55 - Inverter self test failed
    INVERTER_SELF_TEST_A = 55
    # Err 56 - Inverter self test failed
    INVERTER_SELF_TEST_B = 56
    # Err 57 - Inverter ac voltage on output
    INVERTER_AC = 57
    # Err 58 - Inverter self test failed
    INVERTER_SELF_TEST_C = 58
    # Information 65 - Communication warning Lost communication with one of devices
    COMMUNICATION = 65
    # Information 66 - Incompatible device Synchronised charging device configuration issue
    SYNCHRONISATION = 66
    # Err 67 - BMS Connection lost
    BMS = 67
    # Err 68 - Network misconfigured
    NETWORK_A = 68
    # Err 69 - Network misconfigured
    NETWORK_B = 69
    # Err 70 - Network misconfigured
    NETWORK_C = 70
    # Err 71 - Network misconfigured
    NETWORK_D = 71
    # Err 80 - PV Input shutdown
    PV_INPUT_SHUTDOWN_80 = 80
    # Err 81 - PV Input shutdown
    PV_INPUT_SHUTDOWN_81 = 81
    # Err 82 - PV Input shutdown
    PV_INPUT_SHUTDOWN_82 = 82
    # Err 83 - PV Input shutdown
    PV_INPUT_SHUTDOWN_83 = 83
    # Err 84 - PV Input shutdown
    PV_INPUT_SHUTDOWN_84 = 84
    # Err 85 - PV Input shutdown
    PV_INPUT_SHUTDOWN_85 = 85
    # Err 86 - PV Input shutdown
    PV_INPUT_SHUTDOWN_86 = 86
    # Err 87 - PV Input shutdown
    PV_INPUT_SHUTDOWN_87 = 87
    # Err 114 - CPU temperature too high
    CPU_TEMPERATURE = 114
    # Err 116 - Factory calibration data lost
    CALIBRATION_LOST = 116
    # Err 117 - Invalid/incompatible firmware
    FIRMWARE = 117
    # Err 119 - Settings data lost
    SETTINGS = 119
    # Err 121 - Tester fail
    TESTER_FAIL = 121
    # Err 200 - Internal DC voltage error
    INTERNAL_DC_VOLTAGE_A = 200
    # Err 201 - Internal DC voltage error
    INTERNAL_DC_VOLTAGE_B = 201
    # Err 202 - PV residual current sensor self-test failure Internal GFCI sensor error
    SELF_TEST = 202
    # Err 203 - Internal supply voltage error
    INTERNAL_SUPPLY_A = 203
    # Err 205 - Internal supply voltage error
    INTERNAL_SUPPLY_B = 205
    # Err 212 - Internal supply voltage error
    INTERNAL_SUPPLY_C = 212
    # Err 215 - Internal supply voltage error
    INTERNAL_SUPPLY_D = 215


class OffReason(Enum):
    NO_REASON = 0x00000000
    NO_INPUT_POWER = 0x00000001
    SWITCHED_OFF_SWITCH = 0x00000002
    SWITCHED_OFF_REGISTER = 0x00000004
    REMOTE_INPUT = 0x00000008
    PROTECTION_ACTIVE = 0x00000010
    LOAD_OUTPUT_DISABLED = 0x00000014
    PAY_AS_YOU_GO_OUT_OF_CREDIT = 0x00000020
    BMS = 0x00000040
    ENGINE_SHUTDOWN = 0x00000080
    ANALYSING_INPUT_VOLTAGE = 0x00000100


class AlarmReason(Enum):
    NO_ALARM = 0
    LOW_VOLTAGE = 1
    HIGH_VOLTAGE = 2
    LOW_SOC = 4
    LOW_STARTER_VOLTAGE = 8
    HIGH_STARTER_VOLTAGE = 16
    LOW_TEMPERATURE = 32
    HIGH_TEMPERATURE = 64
    MID_VOLTAGE = 128
    OVERLOAD = 256
    DC_RIPPLE = 512
    LOW_V_AC_OUT = 1024
    HIGH_V_AC_OUT = 2048
    SHORT_CIRCUIT = 4096
    BMS_LOCKOUT = 8192


class AlarmNotification(Enum):
    NO_ALARM = 0
    WARNING = 1
    ALARM = 2


# Sourced from Victron extra-manufacturer-data-2022-12-14.pdf
class ACInState(Enum):
    AC_IN_1 = 0
    AC_IN_2 = 1
    NOT_CONNECTED = 2
    UNKNOWN = 3


# Sourced from VE.Direct docs
MODEL_ID_MAPPING = {
    0x1: "VPN",
    0x2: "VBC",
    0x3: "VVC",
    0x4: "VCC",
    0x5: "VCM",
    0x6: "VGM",
    0x7: "VRS",
    0x8: "Free Technics software",
    0x9: "VBC GMDSS",
    0xA: "VPM GMDSS",
    0xB: "BPP",
    0xC: "VBC 48V",
    0xD: "VVC2",
    0xE: "VBC 144V",
    0xF: "VBC2",
    0x10: "VBC 144V",
    0x11: "Lynx Shunt 1000A VE.Net",
    0x100: "BMV to NMEA2000 interface",
    0x101: "Skylla-i Control",
    0x102: "Hybrid Panel",
    0x103: "VE.Bus to NMEA2000 interface",
    0x104: "Skylla-i 24/100 (1+1)",
    0x105: "Skylla-i 24/80A (1+1)",
    0x106: "Skylla-i 24/100 (3)",
    0x107: "Skylla-i 24/80 (3)",
    0x108: "BlueSolar Charger MPPT 150/70",
    0x140: "Ion Control",
    0x141: "Lynx Shunt 1000A VE.Can",
    0x142: "Lynx Ion",
    0x200: "BMV-600S",
    0x201: "BMV-602S",
    0x202: "BMV-600HS",
    0x203: "BMV-700",
    0x204: "BMV-702",
    0x205: "BMV-700H",
    0x211: "BMV PCBA test firmware",
    0x300: "BlueSolar Charger MPPT 70/15",
    0x1110: "Remote panel",
    0x1120: "Remote panel 20MHz",
    0x1121: "Remote panel Dongle 20MHz",
    0x1130: "MK2 20Mhz",
    0x1131: "MK2 Dongle 20Mhz",
    0x1132: "VE.Bus Resetter (based on MK2) 20 Mhz",
    0x1140: "MK2 tachometer 20Mhz",
    0x1145: "BMS 20Mhz",
    0x1150: "Solar switch box",
    0x1160: "USB VEBus grabber",
    0x1170: "MK3",
    0x1421: "Phoenix Charger 12/100",
    0x1422: "Phoenix Charger 12/200",
    0x1431: "Phoenix Charger 24/50",
    0x1432: "Phoenix Charger 24/100",
    0x1700: "Phoenix Multi 12V full power",
    0x1701: "Phoenix Multi 12V half power",
    0x1702: "Phoenix MultiPlus 12V full power",
    0x1703: "MultiCompact 12V low power",
    0x1704: "MultiCompact 12V medium power",
    0x1705: "MultiCompact 12V high power",
    0x1706: "MultiCompactPlus 12V high power",
    0x1707: "MultiCompactPlus 12V medium power",
    0x1710: "Phoenix Multi 24V full power",
    0x1711: "Phoenix Multi 24V half power",
    0x1712: "Phoenix MultiPlus 24V full power",
    0x1713: "MultiCompact 24V low power",
    0x1714: "MultiCompact 24V medium power",
    0x1715: "MultiCompact 24V high power",
    0x1716: "MultiCompactPlus 24V high power",
    0x1717: "MultiCompactPlus 24V medium power",
    0x1730: "Phoenix Multi 120 12V full power",
    0x1731: "Phoenix Multi 120 12V half power",
    0x1732: "Phoenix MultiPlus 120 12V full power",
    0x1740: "Phoenix Multi 120 24V full power",
    0x1741: "Phoenix Multi 120 24V half power",
    0x1742: "Phoenix MultiPlus 120 24V full power",
    0x1750: "Phoenix Multi 48V full power",
    0x1751: "Phoenix Multi 48V half power",
    0x1752: "Phoenix MultiPlus 48V full power",
    0x1800: "Phoenix Multi 12V full power",
    0x1801: "Phoenix Multi 12V half power",
    0x1802: "Phoenix MultiPlus 12V full power",
    0x1803: "MultiCompact 12V low power",
    0x1804: "MultiCompact 12V medium power",
    0x1805: "MultiCompact 12V high power",
    0x1806: "MultiCompactPlus 12V high power",
    0x1807: "MultiCompactPlus 12V medium power",
    0x1808: "Phoenix MultiPlus 12V/2000",
    0x1809: "Phoenix MultiPlus 12V/3000",
    0x1810: "Phoenix Multi 24V full power",
    0x1811: "Phoenix Multi 24V half power",
    0x1812: "Phoenix MultiPlus 24V full power",
    0x1813: "MultiCompact 24V low power",
    0x1814: "MultiCompact 24V medium power",
    0x1815: "MultiCompact 24V high power",
    0x1816: "MultiCompactPlus 24V high power",
    0x1817: "MultiCompactPlus 24V medium power",
    0x1818: "Phoenix MultiPlus 24V/2000",
    0x1830: "Phoenix Multi 120 12V full power",
    0x1831: "Phoenix Multi 120 12V half power",
    0x1832: "Phoenix MultiPlus 120 12V full power",
    0x1836: "MultiCompactPlus 120 12V high power",
    0x1839: "Phoenix MultiPlus 120 12V/3000",
    0x1840: "Phoenix Multi 120 24V full power",
    0x1841: "Phoenix Multi 120 24V half power",
    0x1842: "Phoenix MultiPlus 120 24V full power",
    0x1846: "MultiCompactPlus 120 24V high power",
    0x1850: "Phoenix Multi 48V full power",
    0x1851: "Phoenix Multi 48V half power",
    0x1852: "Phoenix MultiPlus 48V full power",
    0x1856: "MultiCompactPlus 48V high power",
    0x1862: "Phoenix MultiPlus 120 48V full power",
    0x1871: "MultiCompactPlus 12V 2K",
    0x1872: "MultiCompactPlus 24V 2K",
    0x1900: "MultiPlus 12/3000/120-50",
    0x1901: "MultiPlus 12/3000/120-30",
    0x1902: "Phoenix MultiPlus 12V full power",
    0x1903: "Phoenix Multi Compact 12/800/35-16",
    0x1906: "MultiPlus Compact 12/1600/70-16",
    0x1907: "MultiPlus Compact 12/1200/50-16",
    0x1908: "MultiPlus Compact 12/2000/80-30",
    0x1909: "MultiPlus 12/3000/120-16",
    0x1910: "MultiPlus 24/3000/70-50",
    0x1911: "MultiPlus 24/3000/70-30",
    0x1912: "MultiPlus 24/3000/70-16",
    0x1913: "Phoenix Multi Compact 24/800/16-16",
    0x1916: "MultiPlus Compact 24/1600/40-16",
    0x1917: "MultiPlus Compact 24/1200/25-16",
    0x1918: "MultiPlus Compact 24/2000/50-30",
    0x1920: "MultiPlus 48/3000/35-50",
    0x1921: "MultiPlus 48/3000/35-30",
    0x1922: "MultiPlus 48/3000/35-16",
    0x1930: "Quattro 12/5000/200-2x30",
    0x1931: "Quattro 12/3000/120-50/30",
    0x1932: "Quattro 12/5000/200-50/30",
    0x1933: "Quattro 12/5000/220-2x75",
    0x1940: "Quattro 24/5000/120-2x30",
    0x1941: "Quattro 24/3000/70-50/30",
    0x1942: "Quattro 24/5000/120-50/30",
    0x1943: "Quattro 24/8000/200-2x100",
    0x1948: "Quattro 24/5000/120-2x100",
    0x1949: "MultiPlus 24/5000/120-50",
    0x1950: "Quattro 48/5000/70-2x30",
    0x1952: "Quattro 48/5000/70-50/30",
    0x1953: "Quattro 48/10000/140-2x100",
    0x1954: "Quattro 48/8000/110-2x100",
    0x1958: "Quattro 48/5000/70-2x100",
    0x1959: "MultiPlus 48/5000/70-50",
    0x2002: "MultiPlus 12/3000/120-50 120V",
    0x2008: "MultiPlus Compact 12/2000/80-50 120V",
    0x2009: "Phoenix MultiPlus 120 12V/3000",
    0x2012: "MultiPlus 24/3000/70-50 120V",
    0x2018: "MultiPlus Compact 24/2000/50-50 120V",
    0x2022: "Phoenix MultiPlus 120 48V/3000",
    0x2048: "Quattro 24/5000/120-2x100 120V",
    0x2051: "Quattro 48/3000/35-2x50 120V",
    0x2053: "Quattro 48/5000/70-2x100 120V",
    0x2059: "Phoenix MultiPlus 120 48V/5000",
    0x2060: "Phoenix 12/3000/120-50-120/240V",
    0x2062: "MultiPlus Compact 12/2000/80-50(30)-120/240V",
    0x2071: "Quattro 24/5000/120-2x60-120/240V",
    0x2072: "MultiPlus Compact 24/2000/50-50(30)-120/240V",
    0x2080: "Phoenix MultiPlus 120/240 48V/3000 with 50A AC relais",
    0x2101: "Phoenix HF",
    0x2403: "Phoenix 12/800",
    0x2404: "Phoenix 12/1200",
    0x2413: "Phoenix 24/800",
    0x2414: "Phoenix 24/1200",
    0x2423: "Phoenix 48/800",
    0x2424: "Phoenix 48/1200",
    0x2453: "Phoenix 12/800 120V",
    0x2454: "Phoenix 12/1200 120V",
    0x2463: "Phoenix 24/800 120V",
    0x2464: "Phoenix 24/1200 120V",
    0x2473: "Phoenix 48/800 120V",
    0x2474: "Phoenix 48/1200 120V",
    0x2600: "MultiPlus 12/3000/120-50",
    0x2603: "MultiPlus Compact 12/800/35-16",
    0x2605: "MultiPlus-II 12/3000/120-32",
    0x2606: "MultiPlus Compact 12/1600/70-16",
    0x2607: "MultiPlus Compact 12/1200/50-16",
    0x2608: "MultiPlus Compact 12/2000/80-30",
    0x2609: "MultiPlus 12/3000/120-16",
    0x2610: "MultiPlus 24/3000/70-50",
    0x2611: "MultiPlus-II 24/3000/70-32",
    0x2612: "MultiPlus 24/3000/70-16",
    0x2613: "MultiPlus Compact 24/800/16-16",
    0x2614: "MultiPlus 24/5000/120-100",
    0x2615: "MultiPlus-II 24/5000/120-50",
    0x2616: "MultiPlus Compact 24/1600/40-16",
    0x2617: "MultiPlus Compact 24/1200/25-16",
    0x2618: "MultiPlus Compact 24/2000/50-30",
    0x2619: "MultiPlus-II 48/15000/200-100",
    0x2620: "MultiPlus 48/3000/35-50",
    0x2621: "MultiPlus-II 48/8000/110-100",
    0x2622: "MultiPlus 48/3000/35-16",
    0x2623: "MultiPlus-II 48/5000/70-50",
    0x2624: "MultiPlus 48/5000/70-100",
    0x2625: "MultiPlus-II 48/3000/35-32",
    0x2626: "MultiPlus-II 48/5000/70-50",
    0x2627: "MultiPlus-II 48/10000/140-100/100",
    0x2628: "MultiPlus-II 48/3000/35-32",
    0x2629: "MultiPlus-II 48/3000/35-32",
    0x2631: "Quattro 12/3000/120-50/30",
    0x2632: "Quattro-II 12/5000/200-2x50",
    0x2633: "Quattro 12/5000/220-2x75",
    0x2634: "Quattro 12/3000/120-2x50",
    0x2641: "Quattro 24/3000/70-50/30",
    0x2642: "Quattro 24/5000/120-50/30",
    0x2643: "Quattro 24/8000/200-2x100",
    0x2644: "Quattro 24/3000/70-2x50",
    0x2645: "Quattro-II 24/5000/120-2x50",
    0x2648: "Quattro 24/5000/120-2x100",
    0x2649: "MultiPlus 24/5000/120-50",
    0x2651: "Quattro-II 48/5000/70-2x50",
    0x2652: "Quattro 48/5000/70-50/30",
    0x2653: "Quattro 48/10000/140-2x100",
    0x2654: "Quattro 48/8000/110-2x100",
    0x2655: "Quattro 48/8000/110-2x100",
    0x2656: "Quattro 48/15000/200-2x100",
    0x2657: "Quattro 48/5000/70-2x100-S",
    0x2658: "Quattro 48/5000/70-2x100",
    0x2659: "MultiPlus 48/5000/70-50",
    0x2660: "MultiPlus 12/500/20-16",
    0x2661: "MultiPlus 12/800/35-16",
    0x2662: "MultiPlus 12/1200/50-16",
    0x2663: "MultiPlus 12/1600/70-16",
    0x2664: "MultiPlus 12/2000/80-32",
    0x2665: "MultiPlus 24/500/10-16",
    0x2666: "MultiPlus 24/800/16-16",
    0x2667: "MultiPlus 24/1200/25-16",
    0x2668: "MultiPlus 24/1600/40-16",
    0x2669: "MultiPlus 24/2000/50-32",
    0x2670: "MultiPlus 48/500/6-16",
    0x2671: "MultiPlus 48/800/9-16",
    0x2672: "MultiPlus 48/1200/13-16",
    0x2673: "MultiPlus 48/1600/20-16",
    0x2674: "MultiPlus 48/2000/25-32",
    0x2680: "MultiGrid 12/3000/120-50",
    0x2685: "MultiGrid 24/3000/70-50",
    0x2690: "MultiGrid 48/3000/35-50",
    0x2702: "MultiPlus 12/3000/120-50 120V",
    0x2705: "MultiPlus-II 12/3000/120-50 120V",
    0x2708: "MultiPlus Compact 12/2000/80-50 120V",
    0x2711: "MultiPlus-II 24/3000/70-50 120V",
    0x2712: "MultiPlus 24/3000/70-50 120V",
    0x2718: "MultiPlus Compact 24/2000/50-50 120V",
    0x2729: "MultiPlus-II 48/3000/35-50 120V",
    0x2733: "Quattro 12/5000/220-2x100 120V",
    0x2748: "Quattro 24/5000/120-2x100 120V",
    0x2751: "Quattro 48/3000/35-2x50 120V",
    0x2753: "Quattro 48/5000/70-2x100 120V",
    0x2754: "Quattro 48/10000/140-2x100 120V",
    0x2764: "MultiPlus 12/2000/80-50 120V",
    0x2769: "MultiPlus 24/2000/50-50 120V",
    0x2774: "MultiPlus 48/2000/25-50 120V",
    0x2775: "MultiPlus-II 24/3000/70-50 2x120V",
    0x2780: "MultiPlus-II 12/3000/120-50 2x120V",
    0x2781: "Quattro-II 12/3000/120-2x50 2x120V",
    0xA000: "Skylla-IP44/IP65 battery charger",
    0xA001: "Skylla-IP65 12V/70A (1+1)",
    0xA002: "Skylla-IP65 12V/70A (3)",
    0xA003: "Skylla-IP44 12V/60A (1+1)",
    0xA004: "Skylla-IP44 12V/60A (3)",
    0xA005: "Skylla-IP65 24V/35A (1+1)",
    0xA006: "Skylla-IP65 24V/35A (3)",
    0xA007: "Skylla-IP44 24V/30A (1+1)",
    0xA008: "Skylla-IP44 24V/30A (3)",
    0xA010: "Skylla-S battery charger",
    0xA011: "Skylla-S 12V/100A (1+1)",
    0xA012: "Skylla-S 12V/100A (3)",
    0xA013: "Skylla-S 24V/100A (1+1)",
    0xA014: "Skylla-S 24V/100A (3)",
    0xA015: "Skylla-S 24V/50A (1+1)",
    0xA016: "Skylla-S 24V/50A (3)",
    0xA040: "BlueSolar Charger MPPT 75/50",
    0xA041: "BlueSolar Charger MPPT 150/35 rev1",
    0xA042: "BlueSolar Charger MPPT 75/15",
    0xA043: "BlueSolar Charger MPPT 100/15",
    0xA044: "BlueSolar Charger MPPT 100/30 rev1",
    0xA045: "BlueSolar Charger MPPT 100/50 rev1",
    0xA046: "BlueSolar Charger MPPT 150/70",
    0xA047: "BlueSolar Charger MPPT 150/100",
    0xA048: "BlueSolar Charger MPPT 75/50 rev2",
    0xA049: "BlueSolar Charger MPPT 100/50 rev2",
    0xA04A: "BlueSolar Charger MPPT 100/30 rev2",
    0xA04B: "BlueSolar Charger MPPT 150/35 rev2",
    0xA04C: "BlueSolar Charger MPPT 75/10",
    0xA04D: "BlueSolar Charger MPPT 150/45",
    0xA04E: "BlueSolar Charger MPPT 150/60",
    0xA04F: "BlueSolar Charger MPPT 150/85",
    0xA050: "SmartSolar Charger MPPT 250/100",
    0xA051: "SmartSolar Charger MPPT 150/100",
    0xA052: "SmartSolar Charger MPPT 150/85",
    0xA053: "SmartSolar Charger MPPT 75/15",
    0xA054: "SmartSolar Charger MPPT 75/10",
    0xA055: "SmartSolar Charger MPPT 100/15",
    0xA056: "SmartSolar Charger MPPT 100/30",
    0xA057: "SmartSolar Charger MPPT 100/50",
    0xA058: "SmartSolar Charger MPPT 150/35",
    0xA059: "SmartSolar Charger MPPT 150/100 rev2",
    0xA05A: "SmartSolar Charger MPPT 150/85 rev2",
    0xA05B: "SmartSolar Charger MPPT 250/70",
    0xA05C: "SmartSolar Charger MPPT 250/85",
    0xA05D: "SmartSolar Charger MPPT 250/60",
    0xA05E: "SmartSolar Charger MPPT 250/60",
    0xA05F: "SmartSolar Charger MPPT 100/20",
    0xA060: "SmartSolar Charger MPPT 100/20 48V",
    0xA061: "SmartSolar Charger MPPT 150/45",
    0xA062: "SmartSolar Charger MPPT 150/60",
    0xA063: "SmartSolar Charger MPPT 150/70",
    0xA064: "SmartSolar Charger MPPT 250/85 rev2",
    0xA065: "SmartSolar Charger MPPT 250/100 rev2",
    0xA066: "BlueSolar Charger MPPT 100/20",
    0xA067: "BlueSolar Charger MPPT 100/20 48V",
    0xA068: "SmartSolar Charger MPPT 250/60 rev2",
    0xA069: "SmartSolar Charger MPPT 250/70 rev2",
    0xA06A: "SmartSolar Charger MPPT 150/45 rev2",
    0xA06B: "SmartSolar Charger MPPT 150/60 rev2",
    0xA06C: "SmartSolar Charger MPPT 150/70 rev2",
    0xA06D: "SmartSolar Charger MPPT 150/85 rev3",
    0xA06E: "SmartSolar Charger MPPT 150/100 rev3",
    0xA06F: "BlueSolar Charger MPPT 150/45 rev2",
    0xA070: "BlueSolar Charger MPPT 150/60 rev2",
    0xA071: "BlueSolar Charger MPPT 150/70 rev2",
    0xA072: "BlueSolar Charger MPPT 150/45 rev3",
    0xA073: "SmartSolar Charger MPPT 150/45 rev3",
    0xA074: "SmartSolar Charger MPPT 75/10 rev2",
    0xA075: "SmartSolar Charger MPPT 75/15 rev2",
    0xA076: "BlueSolar Charger MPPT 100/30 rev3",
    0xA077: "BlueSolar Charger MPPT 100/50 rev3",
    0xA078: "BlueSolar Charger MPPT 150/35 rev3",
    0xA079: "BlueSolar Charger MPPT 75/10 rev2",
    0xA07A: "BlueSolar Charger MPPT 75/15 rev2",
    0xA07B: "BlueSolar Charger MPPT 100/15 rev2",
    0xA07C: "BlueSolar Charger MPPT 75/10 rev3",
    0xA07D: "BlueSolar Charger MPPT 75/15 rev3",
    0xA07E: "SmartSolar Charger MPPT 100/30 12V",
    0xA0C1: "Lithium Battery Balancer 12V/3.5A",
    0xA0C2: "Lithium Battery Balancer 12V/8A",
    0xA0C3: "Lithium Battery Balancer 24V/3.5A",
    0xA0C4: "Lithium Battery Balancer 12V/2A",
    0xA0E0: "Smart Lithium Battery 12.8V/90Ah",
    0xA0E1: "Smart Lithium Battery 12.8V/60Ah",
    0xA0E2: "Smart Lithium Battery 12.8V/160Ah",
    0xA0E3: "Smart Lithium Battery 12.8V/200Ah",
    0xA0E4: "Smart Lithium Battery 12.8V/300Ah",
    0xA0E5: "Smart Lithium Battery 12.8V/100Ah",
    0xA0E6: "Smart Lithium Battery 12.8V/200Ah",
    0xA0E7: "Smart Lithium Battery 12.8V/300Ah",
    0xA0E8: "Smart Lithium Battery 12.8V/100Ah",
    0xA0E9: "Smart Lithium Battery 12.8V/150Ah",
    0xA0EA: "Smart Lithium Battery 25.6V/200Ah",
    0xA0EB: "Smart Lithium Battery 12.8V/200Ah",
    0xA0EC: "Smart Lithium Battery 12.8V/160Ah",
    0xA0ED: "Smart Lithium Battery 12.8V/50Ah",
    0xA0EE: "Smart Lithium Battery 25.6V/200Ah",
    0xA0EF: "Smart Lithium Battery 25.6V/100Ah",
    0xA0F0: "Smart Lithium Battery 12.8V/330Ah",
    0xA0F1: "Smart Lithium Battery 25.6V/330Ah",
    0xA0F2: "Smart Lithium Battery 12.8V/300Ah",
    0xA100: "BlueSolar Remote Panel",
    0xA101: "BlueSolar Charger MPPT 150/85",
    0xA102: "SmartSolar MPPT VE.Can 150/70",
    0xA103: "SmartSolar MPPT VE.Can 150/45",
    0xA104: "SmartSolar MPPT VE.Can 150/60",
    0xA105: "SmartSolar MPPT VE.Can 150/85",
    0xA106: "SmartSolar MPPT VE.Can 150/100",
    0xA107: "SmartSolar MPPT VE.Can 250/45",
    0xA108: "SmartSolar MPPT VE.Can 250/60",
    0xA109: "SmartSolar MPPT VE.Can 250/70",
    0xA10A: "SmartSolar MPPT VE.Can 250/85",
    0xA10B: "SmartSolar MPPT VE.Can 250/100",
    0xA10C: "SmartSolar MPPT VE.Can 150/70 rev2",
    0xA10D: "SmartSolar MPPT VE.Can 150/85 rev2",
    0xA10E: "SmartSolar MPPT VE.Can 150/100 rev2",
    0xA10F: "BlueSolar MPPT VE.Can 150/100",
    0xA110: "SmartSolar MPPT RS 450/100",
    0xA111: "SmartSolar MPPT RS 450/200",
    0xA112: "BlueSolar MPPT VE.Can 250/70",
    0xA113: "BlueSolar MPPT VE.Can 250/100",
    0xA114: "SmartSolar MPPT VE.Can 250/70 rev2",
    0xA115: "SmartSolar MPPT VE.Can 250/100 rev2",
    0xA116: "SmartSolar MPPT VE.Can 250/85 rev2",
    0xA117: "BlueSolar MPPT VE.Can 150/100 rev2",
    0xA120: "VE.Bus to NMEA2000 interface (rev2)",
    0xA121: "VE.Direct to CAN interface",
    0xA130: "Lynx Ion + Shunt",
    0xA131: "Lynx Smart Shunt 1000A VE.Can",
    0xA140: "PV Inverter (QWACS)",
    0xA141: "PV Inverter (AC Current Sensor)",
    0xA142: "Fronius solar inverters",
    0xA143: "SMA solar inverters",
    0xA144: "SunSpec solar inverters",
    0xA145: "ABB/Fimer solar inverters",
    0xA160: "Tank sensor",
    0xA161: "Generic Tank Input",
    0xA162: "Generic Temperature Input",
    0xA163: "NMEA-0183 GPS",
    0xA164: "NMEA 2000 GPS",
    0xA165: "Generic pulse meter",
    0xA166: "Generic digital input",
    0xA170: "Mppt control",
    0xA171: "Mppt control PCBA test firmware",
    0xA180: "Peak Power Pack 12V 8Ah",
    0xA181: "Peak Power Pack PCBA test firmware",
    0xA182: "VE.Direct Bluetooth Smart Dongle",
    0xA183: "Bootloader for softdevice v7",
    0xA184: "Virtual id for v1 legacy dongle",
    0xA185: "Peak Power Pack 12V 20Ah",
    0xA186: "Peak Power Pack 12V 30Ah",
    0xA187: "Peak Power Pack 12V 40Ah",
    0xA188: "VE.Direct Bluetooth Smart Dongle (Rev2)",
    0xA189: "VE.Direct Bluetooth Smart Dongle (Rev3)",
    0xA190: "SmartSolar Bluetooth Interface",
    0xA191: "SmartSolar Bluetooth Interface (Rev2)",
    0xA192: "BMV-7xx Smart Bluetooth Interface",
    0xA193: "Lynx Ion BMS Bluetooth Interface",
    0xA194: "Phoenix Inverter Smart Bluetooth Interface",
    0xA195: "VE.Can SmartSolar Bluetooth Interface",
    0xA196: "SmartShunt Bluetooth Interface",
    0xA197: "SmartSolar Bluetooth Interface (Rev3)",
    0xA198: "BMV-7xx Smart Bluetooth Interface (Rev2)",
    0xA199: "Lynx Ion BMS Bluetooth Interface (Rev2)",
    0xA19A: "Phoenix Inverter Smart Bluetooth Interface (Rev2)",
    0xA19B: "VE.Can SmartSolar Bluetooth Interface (Rev2)",
    0xA19C: "SmartShunt Bluetooth Interface (Rev2)",
    0xA19D: "SmartShunt Bluetooth Interface (Rev2)",
    0xA19E: "Sun Inverter Bluetooth Interface",
    0xA19F: "All-In-1 Bluetooth Interface",
    0xA1B0: "Smart Energy Meter",
    0xA1B1: "VE.Can Energy Meter",
    0xA200: "Phoenix Inverter",
    0xA201: "Phoenix Inverter 12V 250VA 230V",
    0xA202: "Phoenix Inverter 24V 250VA 230V",
    0xA204: "Phoenix Inverter 48V 250VA 230V",
    0xA211: "Phoenix Inverter 12V 375VA 230V",
    0xA212: "Phoenix Inverter 24V 375VA 230V",
    0xA214: "Phoenix Inverter 48V 375VA 230V",
    0xA221: "Phoenix Inverter 12V 500VA 230V",
    0xA222: "Phoenix Inverter 24V 500VA 230V",
    0xA224: "Phoenix Inverter 48V 500VA 230V",
    0xA231: "Phoenix Inverter 12V 250VA 230V",
    0xA232: "Phoenix Inverter 24V 250VA 230V",
    0xA234: "Phoenix Inverter 48V 250VA 230V",
    0xA235: "Phoenix Sun Inverter 12V 250VA 230V",
    0xA236: "Phoenix Sun Inverter 24V 250VA 230V",
    0xA237: "Phoenix Sun Inverter 48V 250VA 230V",
    0xA239: "Phoenix Inverter 12V 250VA 120V",
    0xA23A: "Phoenix Inverter 24V 250VA 120V",
    0xA23C: "Phoenix Inverter 48V 250VA 120V",
    0xA241: "Phoenix Inverter 12V 375VA 230V",
    0xA242: "Phoenix Inverter 24V 375VA 230V",
    0xA244: "Phoenix Inverter 48V 375VA 230V",
    0xA249: "Phoenix Inverter 12V 375VA 120V",
    0xA24A: "Phoenix Inverter 24V 375VA 120V",
    0xA24C: "Phoenix Inverter 48V 375VA 120V",
    0xA251: "Phoenix Inverter 12V 500VA 230V",
    0xA252: "Phoenix Inverter 24V 500VA 230V",
    0xA254: "Phoenix Inverter 48V 500VA 230V",
    0xA259: "Phoenix Inverter 12V 500VA 120V",
    0xA25A: "Phoenix Inverter 24V 500VA 120V",
    0xA25C: "Phoenix Inverter 48V 500VA 120V",
    0xA261: "Phoenix Inverter 12V 800VA 230V",
    0xA262: "Phoenix Inverter 24V 800VA 230V",
    0xA264: "Phoenix Inverter 48V 800VA 230V",
    0xA269: "Phoenix Inverter 12V 800VA 120V",
    0xA26A: "Phoenix Inverter 24V 800VA 120V",
    0xA26C: "Phoenix Inverter 48V 800VA 120V",
    0xA271: "Phoenix Inverter 12V 1200VA 230V",
    0xA272: "Phoenix Inverter 24V 1200VA 230V",
    0xA274: "Phoenix Inverter 48V 1200VA 230V",
    0xA279: "Phoenix Inverter 12V 1200VA 120V",
    0xA27A: "Phoenix Inverter 24V 1200VA 120V",
    0xA27C: "Phoenix Inverter 48V 1200VA 120V",
    0xA281: "Smart Phoenix Inverter 12V 2000VA 230V",
    0xA282: "Smart Phoenix Inverter 24V 2000VA 230V",
    0xA284: "Smart Phoenix Inverter 48V 2000VA 230V",
    0xA289: "Smart Phoenix Inverter 12V 2000VA 120V",
    0xA28A: "Smart Phoenix Inverter 24V 2000VA 120V",
    0xA28C: "Smart Phoenix Inverter 48V 2000VA 120V",
    0xA291: "Smart Phoenix Inverter 12V 2000VA 230V",
    0xA292: "Smart Phoenix Inverter 24V 2000VA 230V",
    0xA294: "Smart Phoenix Inverter 48V 2000VA 230V",
    0xA299: "Smart Phoenix Inverter 12V 2000VA 120V",
    0xA29A: "Smart Phoenix Inverter 24V 2000VA 120V",
    0xA29C: "Smart Phoenix Inverter 48V 2000VA 120V",
    0xA2A1: "Smart Phoenix Inverter 12V 3000VA 230V",
    0xA2A2: "Smart Phoenix Inverter 24V 3000VA 230V",
    0xA2A4: "Smart Phoenix Inverter 48V 3000VA 230V",
    0xA2A9: "Smart Phoenix Inverter 12V 3000VA 120V",
    0xA2AA: "Smart Phoenix Inverter 24V 3000VA 120V",
    0xA2AC: "Smart Phoenix Inverter 48V 3000VA 120V",
    0xA2B2: "Smart Phoenix Inverter 24V 5000VA 230V",
    0xA2B4: "Smart Phoenix Inverter 48V 5000VA 230V",
    0xA2BA: "Smart Phoenix Inverter 24V 5000VA 120V",
    0xA2BC: "Smart Phoenix Inverter 48V 5000VA 120V",
    0xA2E1: "Phoenix Inverter 12V 800VA 230V",
    0xA2E2: "Phoenix Inverter 24V 800VA 230V",
    0xA2E4: "Phoenix Inverter 48V 800VA 230V",
    0xA2E9: "Phoenix Inverter 12V 800VA 120V",
    0xA2EA: "Phoenix Inverter 24V 800VA 120V",
    0xA2EC: "Phoenix Inverter 48V 800VA 120V",
    0xA2F1: "Phoenix Inverter 12V 1200VA 230V",
    0xA2F2: "Phoenix Inverter 24V 1200VA 230V",
    0xA2F4: "Phoenix Inverter 48V 1200VA 230V",
    0xA2F9: "Phoenix Inverter 12V 1200VA 120V",
    0xA2FA: "Phoenix Inverter 24V 1200VA 120V",
    0xA2FC: "Phoenix Inverter 48V 1200VA 120V",
    0xA300: "Blue Smart Charger - Generic",
    0xA301: "Blue Smart IP65 Charger 12|10",
    0xA302: "Blue Smart IP65 Charger 12|15",
    0xA303: "Blue Smart IP65 Charger 24|8",
    0xA304: "Blue Smart IP65 Charger 12|5",
    0xA305: "Blue Smart IP65 Charger 12|7",
    0xA306: "Blue Smart IP65 Charger 24|5",
    0xA307: "Blue Smart IP65 Charger 12|4",
    0xA308: "Blue Smart IP65s Charger 12|4",
    0xA309: "Blue Smart IP65s Charger 12|5",
    0xA30A: "Blue Smart IP65 Charger 12|25",
    0xA30B: "Blue Smart IP65 Charger 24|13",
    0xA30C: "Blue Smart IP65 Charger 6V/12V-1.1A",
    0xA30D: "Blue Smart IP65s Charger 12/4",
    0xA30E: "Blue Smart IP65s Charger 12/5",
    0xA30F: "Blue Smart IP65 Charger 12/7",
    0xA310: "Blue Smart IP67 Charger 12|7",
    0xA311: "Blue Smart IP67 Charger 12|13",
    0xA312: "Blue Smart IP67 Charger 24|5",
    0xA313: "Blue Smart IP67 Charger 12|17",
    0xA314: "Blue Smart IP67 Charger 12|25",
    0xA315: "Blue Smart IP67 Charger 24|8",
    0xA316: "Blue Smart IP67 Charger 24|12",
    0xA317: "Blue Smart IP67 Charger 12/7",
    0xA318: "Blue Smart IP67 Charger 12/13",
    0xA319: "Blue Smart IP67 Charger 24/5",
    0xA31A: "Blue Smart IP67 Charger 12/17",
    0xA31B: "Blue Smart IP67 Charger 12/25",
    0xA31C: "Blue Smart IP67 Charger 24/8",
    0xA31D: "Blue Smart IP67 Charger 24/12",
    0xA320: "Blue Smart IP22 Charger 12|15 (1)",
    0xA321: "Blue Smart IP22 Charger 12|15 (3)",
    0xA322: "Blue Smart IP22 Charger 12|20 (1)",
    0xA323: "Blue Smart IP22 Charger 12|20 (3)",
    0xA324: "Blue Smart IP22 Charger 12|30 (1)",
    0xA325: "Blue Smart IP22 Charger 12|30 (3)",
    0xA326: "Blue Smart IP22 Charger 24|8 (1)",
    0xA327: "Blue Smart IP22 Charger 24|8 (3)",
    0xA328: "Blue Smart IP22 Charger 24|12 (1)",
    0xA329: "Blue Smart IP22 Charger 24|12 (3)",
    0xA32A: "Blue Smart IP22 Charger 24|16 (1)",
    0xA32B: "Blue Smart IP22 Charger 24|16 (3)",
    0xA32C: "Blue Smart IP22 Charger 12/15 (1)",
    0xA32D: "Blue Smart IP22 Charger 12/15 (3)",
    0xA32E: "Blue Smart IP22 Charger 12/20 (1)",
    0xA32F: "Blue Smart IP22 Charger 12/20 (3)",
    0xA330: "Blue Smart IP22 Charger 12/30 (1)",
    0xA331: "Blue Smart IP22 Charger 12/30 (3)",
    0xA332: "Blue Smart IP22 Charger 24/8 (1)",
    0xA333: "Blue Smart IP22 Charger 24/8 (3)",
    0xA334: "Blue Smart IP22 Charger 24/12 (1)",
    0xA335: "Blue Smart IP22 Charger 24/12 (3)",
    0xA336: "Blue Smart IP22 Charger 24/16 (1)",
    0xA337: "Blue Smart IP22 Charger 24/16 (3)",
    0xA338: "Blue Smart IP65 Charger 12/10",
    0xA339: "Blue Smart IP65 Charger 12/15",
    0xA33A: "Blue Smart IP65 Charger 24/5",
    0xA33B: "Blue Smart IP65 Charger 24/8",
    0xA33C: "Blue Smart IP65 Charger 12/5",
    0xA340: "Phoenix Smart IP43 Charger 12|50 (1+1) 230V",
    0xA341: "Phoenix Smart IP43 Charger 12|50 (3) 230V",
    0xA342: "Phoenix Smart IP43 Charger 24|25 (1+1) 230V",
    0xA343: "Phoenix Smart IP43 Charger 24|25 (3) 230V",
    0xA344: "Phoenix Smart IP43 Charger 12|30 (1+1) 230V",
    0xA345: "Phoenix Smart IP43 Charger 12|30 (3) 230V",
    0xA346: "Phoenix Smart IP43 Charger 24|16 (1+1) 230V",
    0xA347: "Phoenix Smart IP43 Charger 24|16 (3) 230V",
    0xA350: "Phoenix Smart IP43 Charger 12|50 (1+1) 120-240V",
    0xA351: "Phoenix Smart IP43 Charger 12|50 (3) 120-240V",
    0xA352: "Phoenix Smart IP43 Charger 24|25 (1+1) 120-240V",
    0xA353: "Phoenix Smart IP43 Charger 24|25 (3) 120-240V",
    0xA354: "Phoenix Smart IP43 Charger 12|30 (1+1) 120-240V",
    0xA355: "Phoenix Smart IP43 Charger 12|30 (3) 120-240V",
    0xA356: "Phoenix Smart IP43 Charger 24|16 (1+1) 120-240V",
    0xA357: "Phoenix Smart IP43 Charger 24|16 (3) 120-240V",
    0xA360: "IMPULSE-II 24/6 Smart IP44",
    0xA361: "IMPULSE-II 24/8 Smart IP44",
    0xA362: "IMPULSE-II 24/6 Smart IP65",
    0xA363: "IMPULSE-II 24/8 Smart IP65",
    0xA364: "IMPULSE-II 24/6 Smart IP44",
    0xA365: "IMPULSE-II 24/8 Smart IP44",
    0xA366: "IMPULSE-II 24/12 Smart IP65",
    0xA367: "IMPULSE-II 24/11 Smart IP44",
    0xA368: "IMPULSE-II 24/8 Smart IP44",
    0xA369: "IMPULSE-II 24/6 Smart IP44",
    0xA36A: "IMPULSE-II 24/8 Smart IP65",
    0xA36B: "IMPULSE-II 24/6 Smart IP65",
    0xA37D: "Vector 12/20 Smart",
    0xA37E: "IMPULSE-II L 12/20 Smart",
    0xA37F: "IMPULSE-II L 12/20 Smart",
    0xA380: "BMV-710 Smart",
    0xA381: "BMV-712 Smart",
    0xA382: "BMV-710H Smart",
    0xA383: "BMV-712 Smart",
    0xA389: "SmartShunt 500A/50mV",
    0xA38A: "SmartShunt 1000A/50mV",
    0xA38B: "SmartShunt 2000A/50mV",
    0xA38C: "SmartShunt IP67 500A/50mV",
    0xA38D: "SmartShunt IP67 1000A/50mV",
    0xA38E: "SmartShunt IP67 2000A/50mV",
    0xA390: "Lynx Ion BMS General",
    0xA391: "Lynx Ion BMS 150A",
    0xA392: "Lynx Ion BMS 400A",
    0xA393: "Lynx Ion BMS 600A",
    0xA394: "Lynx Ion BMS 1000A",
    0xA3A0: "VE.Bus smart dongle",
    0xA3A4: "Smart Battery Sense",
    0xA3A5: "Smart Battery Sense (Rev2)",
    0xA3B0: "Smart BatteryProtect 12/24V-65A",
    0xA3B1: "Smart BatteryProtect 12/24V-100A",
    0xA3B2: "Smart BatteryProtect 12/24V-220A",
    0xA3B3: "Smart BatteryProtect 48V-100A",
    0xA3C0: "Orion Smart 12V/12V-18A DC-DC Converter",
    0xA3C1: "Orion Smart 12V/24V-10A DC-DC Converter",
    0xA3C2: "Orion Smart 24V/12V-20A DC-DC Converter",
    0xA3C3: "Orion Smart 24V/24V-12A DC-DC Converter",
    0xA3C4: "Orion Smart 24V/48V-6A DC-DC Converter",
    0xA3C5: "Orion Smart 48V/12V-20A DC-DC Converter",
    0xA3C6: "Orion Smart 48V/24V-12A DC-DC Converter",
    0xA3C7: "Orion Smart 48V/48V-6A DC-DC Converter",
    0xA3C8: "Orion Smart 12V/12V-30A DC-DC Converter",
    0xA3C9: "Orion Smart 12V/24V-15A DC-DC Converter",
    0xA3CA: "Orion Smart 24V/12V-30A DC-DC Converter",
    0xA3CB: "Orion Smart 24V/24V-17A DC-DC Converter",
    0xA3CC: "Orion Smart 24V/48V-8.5A DC-DC Converter",
    0xA3CD: "Orion Smart 48V/12V-30A DC-DC Converter",
    0xA3CE: "Orion Smart 48V/24V-16A DC-DC Converter",
    0xA3CF: "Orion Smart 48V/48V-8A DC-DC Converter",
    0xA3D0: "Orion Smart 12V/12V-30A Buck-Boost Converter",
    0xA3D1: "Orion Smart 12V/24V-15A Buck-Boost Converter",
    0xA3D2: "Orion Smart Orion 24V/12V-30A Buck-Boost Converter",
    0xA3D3: "Orion Smart Orion 24V/24V-17A Buck-Boost Converter",
    0xA3E0: "Smart BMS CL 12-100",
    0xA3E5: "Lynx Smart BMS 500",
    0xA3E6: "Lynx Smart BMS 1000",
    0xA3E8: "Smart BMS 12-200",
    0xA3EC: "smallBMS",
    0xA3F0: "Smart Buckboost 12V/12V-50A non-iso DC-DC charger",
    0xA400: "MultiC - Generic",
    0xA401: "Inverter RS Solar 48V/6000VA/80A",
    0xA402: "Inverter RS 48V/6000VA",
    0xA441: "Multi RS Solar 48V/6000VA/100A",
    0xA442: "Multi RS Solar 48V/6000VA/100A",
    0xA443: "Multi RS Solar 48V/6000VA/100A",
    0xA444: "Multi RS Solar 48V/6000VA/100A",
    0xA480: "Multi 15kVA 3phase",
    0xA4C0: "Transfer Switch - Generic id",
    0xA4C1: "Transfer Switch 3 Phase 2 in 1 out 80A",
    0xA501: "MultiPlus-X Smart 12V/3000VA/120A",
    0xB000: "Valence XP Battery",
    0xB001: "Valence BMS",
    0xB002: "Carlo Gavazzi EM24 Energy Meter",
    0xB003: "Redflow ZBM 2 Battery",
    0xB004: "LG resu battery",
    0xB005: "BMZ battery",
    0xB006: "Carlo Gavazzi virtual PV Inverter (on EM24)",
    0xB007: "CAN-bus BMS battery",
    0xB008: "Murata battery",
    0xB009: "Pylontech battery",
    0xB00A: "BYD B-Box Pro battery",
    0xB00B: "PureDrive battery",
    0xB00C: "Carlo Gavazzi ET 112 Energy Meter",
    0xB00D: "Carlo Gavazzi ET 340 Energy Meter",
    0xB00E: "ZCell BMS",
    0xB00F: "Energy Tube EMSC2 battery",
    0xB010: "Mercedes Benz Energy battery",
    0xB011: "Carlo Gavazzi virtual PV Inverter (on ET340)",
    0xB012: "FIAMM SoNick 48TL battery",
    0xB013: "SSS DC Energy Meter/Switch",
    0xB014: "Freedom WON battery",
    0xB015: "BYD B-Box L battery",
    0xB016: "Discover AES battery",
    0xB017: "Carlo Gavazzi EM24 Ethernet Energy Meter",
    0xB018: "Smappee Power Box",
    0xB019: "BYD Premium LV battery",
    0xB020: "BlueNova battery",
    0xB021: "BSLBATT battery",
    0xB022: "REC-BMS battery",
    0xB023: "Eastron SDM630 Energy Meter",
    0xB024: "Freedom WON eTower battery",
    0xB025: "Dyness battery",
    0xB026: "Carlo Gavazzi EM540 Energy Meter",
    0xB027: "Carlo Gavazzi virtual PV Inverter (on EM540)",
    0xB028: "Cegasa battery",
    0xB029: "Pylontech Pelio-L battery",
    0xB030: "IMT Si-RS485 Series Solar Irradiance Sensor",
    0xB031: "Carlo Gavazzi EM300 Spec 27 Energy Meter",
    0xB032: "Carlo Gavazzi virtual PV Inverter (on EM300 Spec 27)",
    0xB033: "ABB B-Series Energy Meter",
    0xB034: "Shelly EM/3EM Energy Meter",
    0xB040: "Fischer Panda Genset",
    0xB041: "WATT Imperium Fuel Cell 3.0",
    0xB042: "Bornay Windplus",
    0xB043: "WATT Imperium Fuel Cell 4.0",
    0xB050: "123 SmartBMS",
    0xB051: "Hubble battery",
    0xB060: "Oceanvolt Display 2",
    0xB061: "Oceanvolt ServoProp",
    0xB070: "Volturnus Wind Turbine Voltage Limiter",
    0xB071: "EConnect Distribution Box",
    0xB080: "Wakespeed WS500 Alternator Regulator",
    0xB081: "Wakespeed WS3000 DCDC EMS",
    0xB0C0: "MG BMS 24-96V General",
    0xB0C1: "MG BMS 24-48V/150A",
    0xB0C2: "MG BMS 24-48V/400A",
    0xB0C3: "MG BMS 24-48V/600A",
    0xB0C4: "MG BMS 24-48V/1000A",
    0xB0C5: "MG BMS 72V/400A",
    0xB0C6: "MG BMS 96V/600A",
    0xB0C7: "MG BMS 72-96V/500A",
    0xB0D0: "MG BMS 12V General",
    0xB0D1: "MG BMS 12V/150",
    0xB0D2: "MG BMS 12V/400A",
    0xB0D3: "MG BMS 12V/600A",
    0xB0D4: "MG BMS 12V/1000A",
    0xB0D8: "MG BMS 48-900V General",
    0xB0D9: "MG BMS 48-900V/300A",
    0xB0DA: "MG BMS 48-900V/500A",
    0xB0E0: "MG SmartLink MX",
    0xB0E1: "MG SmartLink Connect",
    0xB0E2: "MG SmartLink PLC",
    0xC000: "VGR, VGR2 or VER",
    0xC001: "Color Control",
    0xC002: "Venus GX",
    0xC003: "Generic Venus Device",
    0xC004: "VE.Direct LoRaWAN",
    0xC005: "VE.Direct LoRaWAN Smart",
    0xC006: "Octo GX",
    0xC007: "EasySolar-II",
    0xC008: "MultiPlus-II",
    0xC009: "Maxi GX",
    0xC00A: "Cerbo GX",
    0xC00B: "EasySolar-II",
    0xC00C: "MultiPlus-II",
    0xC00D: "Maxi GX",
    0xC00E: "EasySolar-II",
    0xC00F: "MultiPlus-II",
    0xC010: "Maxi GX",
    0xC011: "SHS400",
    0xC012: "Cerbo GX",
    0xC013: "Ekrano GX",
    0xC014: "Cerbo-S GX",
    0xC020: "VE.Direct LoRaWAN",
    0xC021: "Global Link 520",
    0xC024: "EV Charge Station 32A",
    0xC025: "EV Charge Station 32A",
    0xC026: "EV Charge Station 32A NS",
    0xC028: "GX Tank 140",
    0xC029: "RuuviTag",
    0xC02A: "Mopeka sensor",
    0xC030: "SmartShunt IP65 500A/50mV",
    0xC031: "SmartShunt IP65 1000A/50mV",
    0xC032: "SmartShunt IP65 2000A/50mV",
    0xC033: "All-In-1 Smart",
    0xC034: "BMV-800 Smart",
    0xC035: "SmartShunt IP65 500A/50mV",
    0xC036: "SmartShunt IP65 1000A/50mV",
    0xC037: "SmartShunt IP65 2000A/50mV",
}


class DeviceData:
    def __init__(self, model_id: int, data: Dict[str, Any]) -> None:
        self._model_id: int = model_id
        self._data: Dict[str, Any] = data

    def get_model_name(self) -> str:
        return MODEL_ID_MAPPING.get(
            self._model_id, f"<Unknown device: {self._model_id}>"
        )


@dataclass
class AdvertisementContainer:
    prefix: int
    model_id: int
    readout_type: int
    iv: int
    encrypted_data: bytes


class Device(abc.ABC):
    data_type: Type[DeviceData] = DeviceData

    def parse_container(self, data) -> AdvertisementContainer:
        return AdvertisementContainer(
            prefix=struct.unpack("<H", data[:2])[0],
            model_id=struct.unpack("<H", data[2:4])[0],
            readout_type=struct.unpack("<B", data[4:5])[0],
            iv=struct.unpack("<H", data[5:7])[0],
            encrypted_data=data[7:],
        )

    def __init__(self, advertisement_key: str):
        self.advertisement_key = advertisement_key

    def get_model_id(self, data: bytes) -> int:
        return self.parse_container(data).model_id

    def decrypt(self, data: bytes) -> bytes:
        container = self.parse_container(data)

        advertisement_key = bytes.fromhex(self.advertisement_key)

        # The first data byte is a key check byte
        if container.encrypted_data[0] != advertisement_key[0]:
            raise AdvertisementKeyMismatchError("Incorrect advertisement key")

        ctr = Counter.new(128, initial_value=container.iv, little_endian=True)

        cipher = AES.new(
            advertisement_key,
            AES.MODE_CTR,
            counter=ctr,
        )
        return cipher.decrypt(pad(container.encrypted_data[1:], 16))

    def parse(self, data: bytes) -> DeviceData:
        decrypted = self.decrypt(data)
        parsed = self.parse_decrypted(decrypted)
        model = self.get_model_id(data)
        return self.data_type(model, parsed)

    @abc.abstractmethod
    def parse_decrypted(self, decrypted: bytes) -> dict:
        pass


def kelvin_to_celsius(temp_in_kelvin: float) -> float:
    return round(temp_in_kelvin - 273.15, 2)


# Reads bit-field structures in the order in which they are packed in
# Victron Extra Manufacturer Data from LSB to MSB.
class BitReader:
    def __init__(self, data: bytes):
        self._data = data
        self._index = 0

    def read_bit(self) -> int:
        bit = (self._data[self._index >> 3] >> (self._index & 7)) & 1
        self._index += 1
        return bit

    def read_unsigned_int(self, num_bits: int) -> int:
        value = 0
        for position in range(0, num_bits):
            value |= self.read_bit() << position
        return value

    def read_signed_int(self, num_bits: int) -> int:
        return BitReader.to_signed_int(self.read_unsigned_int(num_bits), num_bits)

    @staticmethod
    def to_signed_int(value: int, num_bits: int) -> int:
        return value - (1 << num_bits) if value & (1 << (num_bits - 1)) else value
