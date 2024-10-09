import abc
import struct
from dataclasses import dataclass
from enum import Enum, Flag
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


class OffReason(Flag):
    NO_REASON = 0x00000000
    NO_INPUT_POWER = 0x00000001
    SWITCHED_OFF_SWITCH = 0x00000002
    SWITCHED_OFF_REGISTER = 0x00000004
    REMOTE_INPUT = 0x00000008
    PROTECTION_ACTIVE = 0x00000010
    PAY_AS_YOU_GO_OUT_OF_CREDIT = 0x00000020
    BMS = 0x00000040
    ENGINE_SHUTDOWN = 0x00000080
    ANALYSING_INPUT_VOLTAGE = 0x00000100


class AlarmReason(Flag):
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
    0x203: "BMV-700",
    0x204: "BMV-702",
    0x205: "BMV-700H",
    0x0300: "BlueSolar MPPT 70|15",
    0xA040: "BlueSolar MPPT 75|50",
    0xA041: "BlueSolar MPPT 150|35",
    0xA042: "BlueSolar MPPT 75|15",
    0xA043: "BlueSolar MPPT 100|15",
    0xA044: "BlueSolar MPPT 100|30",
    0xA045: "BlueSolar MPPT 100|50",
    0xA046: "BlueSolar MPPT 150|70",
    0xA047: "BlueSolar MPPT 150|100",
    0xA049: "BlueSolar MPPT 100|50 rev2",
    0xA04A: "BlueSolar MPPT 100|30 rev2",
    0xA04B: "BlueSolar MPPT 150|35 rev2",
    0xA04C: "BlueSolar MPPT 75|10",
    0xA04D: "BlueSolar MPPT 150|45",
    0xA04E: "BlueSolar MPPT 150|60",
    0xA04F: "BlueSolar MPPT 150|85",
    0xA050: "SmartSolar MPPT 250|100",
    0xA051: "SmartSolar MPPT 150|100",
    0xA052: "SmartSolar MPPT 150|85",
    0xA053: "SmartSolar MPPT 75|15",
    0xA054: "SmartSolar MPPT 75|10",
    0xA055: "SmartSolar MPPT 100|15",
    0xA056: "SmartSolar MPPT 100|30",
    0xA057: "SmartSolar MPPT 100|50",
    0xA058: "SmartSolar MPPT 150|35",
    0xA059: "SmartSolar MPPT 150|100 rev2",
    0xA05A: "SmartSolar MPPT 150|85 rev2",
    0xA05B: "SmartSolar MPPT 250|70",
    0xA05C: "SmartSolar MPPT 250|85",
    0xA05D: "SmartSolar MPPT 250|60",
    0xA05E: "SmartSolar MPPT 250|45",
    0xA05F: "SmartSolar MPPT 100|20",
    0xA060: "SmartSolar MPPT 100|20 48V",
    0xA061: "SmartSolar MPPT 150|45",
    0xA062: "SmartSolar MPPT 150|60",
    0xA063: "SmartSolar MPPT 150|70",
    0xA064: "SmartSolar MPPT 250|85 rev2",
    0xA065: "SmartSolar MPPT 250|100 rev2",
    0xA066: "BlueSolar MPPT 100|20",
    0xA067: "BlueSolar MPPT 100|20 48V",
    0xA068: "SmartSolar MPPT 250|60 rev2",
    0xA069: "SmartSolar MPPT 250|70 rev2",
    0xA06A: "SmartSolar MPPT 150|45 rev2",
    0xA06B: "SmartSolar MPPT 150|60 rev2",
    0xA06C: "SmartSolar MPPT 150|70 rev2",
    0xA06D: "SmartSolar MPPT 150|85 rev3",
    0xA06E: "SmartSolar MPPT 150|100 rev3",
    0xA06F: "BlueSolar MPPT 150|45 rev2",
    0xA070: "BlueSolar MPPT 150|60 rev2",
    0xA071: "BlueSolar MPPT 150|70 rev2",
    0xA0EC: "SmartLithium Battery 12V/160Ah",
    0xA0EE: "SmartLithium Battery 24V/200Ah",
    0xA0F0: "SmartLithium Battery 12V/330Ah",
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
    0xA112: "BlueSolar MPPT VE.Can 250/70",
    0xA113: "BlueSolar MPPT VE.Can 250/100",
    0xA114: "SmartSolar MPPT VE.Can 250/70 rev2",
    0xA115: "SmartSolar MPPT VE.Can 250/100 rev2",
    0xA116: "SmartSolar MPPT VE.Can 250/85 rev2",
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
    0xA281: "Phoenix Inverter 12V 1600VA 230V",
    0xA282: "Phoenix Inverter 24V 1600VA 230V",
    0xA284: "Phoenix Inverter 48V 1600VA 230V",
    0xA291: "Phoenix Inverter 12V 2000VA 230V",
    0xA292: "Phoenix Inverter 24V 2000VA 230V",
    0xA294: "Phoenix Inverter 48V 2000VA 230V",
    0xA2A1: "Phoenix Inverter 12V 3000VA 230V",
    0xA2A2: "Phoenix Inverter 24V 3000VA 230V",
    0xA2A4: "Phoenix Inverter 48V 3000VA 230V",
    0xA340: "Phoenix Smart IP43 Charger 12|50 (1+1)",
    0xA341: "Phoenix Smart IP43 Charger 12|50 (3)",
    0xA342: "Phoenix Smart IP43 Charger 24|25 (1+1)",
    0xA343: "Phoenix Smart IP43 Charger 24|25 (3)",
    0xA344: "Phoenix Smart IP43 Charger 12|30 (1+1)",
    0xA345: "Phoenix Smart IP43 Charger 12|30 (3)",
    0xA346: "Phoenix Smart IP43 Charger 24|16 (1+1)",
    0xA347: "Phoenix Smart IP43 Charger 24|16 (3)",
    0xA3B0: "Smart BatteryProtect 12/24V-65A",
    0xA381: "BMV-712 Smart",
    0xA382: "BMV-710H Smart",
    0xA383: "BMV-712 Smart Rev2",
    0xA389: "SmartShunt 500A/50mV",
    0xA38A: "SmartShunt 1000A/50mV",
    0xA38B: "SmartShunt 2000A/50mV",
    0xA3A4: "Smart Battery Sense",
    0xA3A5: "Smart Battery Sense",
    0xA3C0: "Orion Smart 12V|12V-18A Isolated DC-DC Charger",
    0xA3C8: "Orion Smart 12V|12V-30A Isolated DC-DC Charger",
    0xA3D0: "Orion Smart 12V|12V-30A Non-isolated DC-DC Charger",
    0xA3C1: "Orion Smart 12V|24V-10A Isolated DC-DC Charger",
    0xA3C9: "Orion Smart 12V|24V-15A Isolated DC-DC Charger",
    0xA3D1: "Orion Smart 12V|24V-15A Non-isolated DC-DC Charger",
    0xA3C2: "Orion Smart 24V|12V-20A Isolated DC-DC Charger",
    0xA3CA: "Orion Smart 24V|12V-30A Isolated DC-DC Charger",
    0xA3D2: "Orion Smart 24V|12V-30A Non-isolated DC-DC Charger",
    0xA3C3: "Orion Smart 24V|24V-12A Isolated DC-DC Charger",
    0xA3CB: "Orion Smart 24V|24V-17A Isolated DC-DC Charger",
    0xA3D3: "Orion Smart 24V|24V-17A Non-isolated DC-DC Charger",
    0xA3C4: "Orion Smart 24V|48V-6A Isolated DC-DC Charger",
    0xA3CC: "Orion Smart 24V|48V-8.5A Isolated DC-DC Charger",
    0xA3C5: "Orion Smart 48V|12V-20A Isolated DC-DC Charger",
    0xA3CD: "Orion Smart 48V|12V-30A Isolated DC-DC Charger",
    0xA3C6: "Orion Smart 48V|24V-12A Isolated DC-DC Charger",
    0xA3CE: "Orion Smart 48V|24V-16A Isolated DC-DC Charger",
    0xA3C7: "Orion Smart 48V|48V-6A Isolated DC-DC Charger",
    0xA3CF: "Orion Smart 48V|48V-8.5A Isolated DC-DC Charger",
    0xA3F0: "Orion XS 12V|12V-50A",
    0xA3E6: "Lynx Smart BMS 1000",
    0x2780: "Victron Multiplus II 12/3000/120-50 2x120V",
    0xC030: "SmartShunt IP65 500A/50mV",
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
