from construct import BitsInteger, BitStruct, ByteSwapped, Padding

from victron_ble.devices.base import Device, DeviceData


class LynxSmartBMSData(DeviceData):
    def get_error_flags(self) -> int:
        """
        Get the raw error_flags field (meaning not documented).
        """
        return self._data["error_flags"]

    def get_remaining_mins(self) -> float:
        """
        Return the number of remaining minutes of battery life in minutes
        """
        return self._data["remaining_mins"]

    def get_voltage(self) -> float:
        """
        Return the voltage in volts
        """
        return self._data["voltage"]

    def get_current(self) -> float:
        """
        Return the current in amps
        """
        return self._data["current"]

    def get_io_status(self) -> int:
        """
        Get the raw io_status field (meaning not documented).
        """
        return self._data["io_status"]

    def get_alarm_flags(self) -> int:
        """
        Get the raw alarm_flags field (meaning not documented).
        """
        return self._data["alarm_flags"]

    def get_soc(self) -> float:
        """
        Return the state of charge in percentage
        """
        return self._data["soc"]

    def get_consumed_ah(self) -> float:
        """
        Return the consumed energy in amp hours
        """
        return self._data["consumed_ah"]

    def get_battery_temperature(self) -> int:
        """
        Return the temperature in Celsius if the aux input is set to temperature
        """
        return self._data["battery_temperature"]


class LynxSmartBMS(Device):
    data_type = LynxSmartBMSData

    # https://community.victronenergy.com/questions/187303/victron-bluetooth-advertising-protocol.html
    # Reverse the entire packet, because non-aligned integers are packed
    # little-endian
    PACKET = ByteSwapped(
        BitStruct(
            Padding(1),  # unused
            "battery_temperature" / BitsInteger(7),  # -40..86C
            "consumed_ah" / BitsInteger(20),  # -104857..0Ah
            "soc" / BitsInteger(10),  # 0..100%
            "alarm_flags" / BitsInteger(18),
            "io_status" / BitsInteger(16),
            "current" / BitsInteger(16, signed=True),  # -3276.8..3276.6 A
            "voltage" / BitsInteger(16),  # -327.68..327.66 V
            "remaining_mins" / BitsInteger(16),  # 0..45.5 days (in mins)
            "error_flags" / BitsInteger(8),
        ),
    )

    def parse_decrypted(self, decrypted: bytes) -> dict:
        pkt = self.PACKET.parse(decrypted[:20])

        parsed = {
            "error_flags": pkt.error_flags,
            "remaining_mins": (
                pkt.remaining_mins if pkt.remaining_mins != 0xFFFF else None
            ),
            "voltage": pkt.voltage / 100 if pkt.voltage != 0x7FFF else None,
            "current": pkt.current / 10 if pkt.current != 0x7FFF else None,
            "io_status": pkt.io_status,
            "alarm_flags": pkt.alarm_flags,
            "soc": pkt.soc / 10.0 if pkt.soc != 0x3FFF else None,
            "consumed_ah": pkt.consumed_ah / 10 if pkt.consumed_ah != 0xFFFFF else None,
            "battery_temperature": (
                (pkt.battery_temperature - 40)
                if pkt.battery_temperature != 0x7F
                else None
            ),
        }

        return parsed
