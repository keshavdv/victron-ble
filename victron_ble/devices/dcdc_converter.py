from construct import GreedyBytes, Int8ul, Int16sl, Int16ul, Int32ul, Struct

from victron_ble.devices.base import (
    ChargerError,
    Device,
    DeviceData,
    OffReason,
    OperationMode,
)


class DcDcConverterData(DeviceData):
    def get_charge_state(self) -> OperationMode:
        """
        Return an enum indicating the current charging state
        """
        return self._data["device_state"]

    def get_charger_error(self) -> ChargerError:
        """
        Return an enum indicating the error code
        """
        return self._data["charger_error"]

    def get_input_voltage(self) -> float:
        """
        Return the input voltage in volts
        """
        return self._data["input_voltage"]

    def get_output_voltage(self) -> float:
        """
        Return the output voltage in volts
        """
        return self._data["output_voltage"]

    def get_off_reason(self) -> OffReason:
        """
        Return an error code stating the reason for the output to be off
        """
        return self._data["off_reason"]


class DcDcConverter(Device):
    data_type = DcDcConverterData

    PACKET = Struct(
        # Charge State:   0 - Off
        #                 3 - Bulk
        #                 4 - Absorption
        #                 5 - Float
        "device_state" / Int8ul,
        # Charger Error Code
        "charger_error" / Int8ul,
        # Input voltage reading in 0.01V increments
        "input_voltage" / Int16ul,
        # Output voltage in 0.01V
        "output_voltage" / Int16sl,
        # Reason for Charger Off
        "off_reason" / Int32ul,
        GreedyBytes,
    )

    def parse_decrypted(self, decrypted: bytes) -> dict:
        pkt = self.PACKET.parse(decrypted)

        return {
            "device_state": OperationMode(pkt.device_state),
            "charger_error": ChargerError(pkt.charger_error),
            "input_voltage": pkt.input_voltage / 100,
            "output_voltage": (
                0 if pkt.output_voltage == 0x7FFF else pkt.output_voltage / 100
            ),
            "off_reason": OffReason(pkt.off_reason),
        }
