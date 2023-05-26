from construct import Bytes, GreedyBytes, Int8ul, Int16sl, Int16ul, Struct

from victron_ble.devices.base import ACInState, Device, DeviceData, OperationMode


class VEBusData(DeviceData):
    def get_device_state(self) -> OperationMode:
        """
        Return an enum indicating the device state
        """
        return self._data["device_state"]

    def get_ac_in_state(self) -> ACInState:
        """
        Return an enum indicating the current ac power state
        """
        return self._data["ac_in_state"]

    def get_ac_in_power(self) -> float:
        """
        Return the current AC power draw
        """
        return self._data["ac_in_power"]

    def get_ac_out_power(self) -> float:
        """
        Return the current AC power output
        """
        return self._data["ac_out_power"]

    def get_battery_current(self) -> float:
        """
        Return the battery current in amps (positive for charging, negative for inverting)
        """
        return self._data["battery_current"]

    def get_battery_voltage(self) -> float:
        """
        Return the battery voltage in volts
        """
        return self._data["battery_voltage"]

    def get_battery_temperature(self) -> float:
        """
        Return the battery temperature in degrees celcius
        """
        return self._data["battery_temperature"]

    def get_soc(self) -> float:
        """
        Return the battery state of charge as a percentage
        """
        return self._data["soc"]


class VEBus(Device):
    data_type = VEBusData

    PACKET = Struct(
        # Device state (docs do not explain how to interpret)
        "device_state" / Int8ul,
        # VE.Bus error (docs do not explain how to interpret)
        "vebus_error" / Int8ul,
        # Battery charging Current reading in 0.1A increments
        "battery_current" / Int16sl,
        # Battery voltage reading in 0.01V increments (14 bits)
        # Active AC in state (enum) (2 bits)
        "battery_voltage_and_ac_in_state" / Int16ul,
        # Active AC in power in 1W increments (19 bits, signed)
        # AC out power in 1W increments (19 bits, signed)
        # Alarm (enum but docs say "to be defined") (2 bits)
        "ac_in_and_ac_out_power" / Bytes(5),
        # Battery temperature in 1 degree celcius increments (7 bits)
        # Battery state of charge in 1% increments (7 bits)
        "battery_temperature_and_soc" / Bytes(2),
        GreedyBytes,
    )

    def parse_decrypted(self, decrypted: bytes) -> dict:
        pkt = self.PACKET.parse(decrypted)

        battery_voltage = pkt.battery_voltage_and_ac_in_state & 0x3FFF

        ac_in_state = pkt.battery_voltage_and_ac_in_state >> 14

        ac_in_bytes = int.from_bytes(pkt.ac_in_and_ac_out_power[0:3], "little")
        ac_in_power = ac_in_bytes & 0x03FFFF
        if ac_in_bytes & 0x40000:
            ac_in_power *= -1

        ac_out_bytes = int.from_bytes(pkt.ac_in_and_ac_out_power[2:5], "little") >> 2
        ac_out_power = (ac_out_bytes >> 1) & 0x07FFFF
        if ac_out_bytes & 0b1:
            ac_out_power *= -1

        # per extra-manufacturer-data-2022-12-14.pdf, the actual temp is 40 degrees less
        battery_temperature = (pkt.battery_temperature_and_soc[0] & 0x46) - 40

        # confusingly, soc is split across the byte boundary
        soc = ((pkt.battery_temperature_and_soc[1] & 0x3F) << 1) + (
            pkt.battery_temperature_and_soc[0] >> 7
        )

        return {
            "device_state": OperationMode(pkt.device_state),
            "battery_voltage": battery_voltage / 100,
            "battery_current": pkt.battery_current / 10,
            "ac_in_state": ACInState(ac_in_state),
            "ac_in_power": ac_in_power,
            "ac_out_power": ac_out_power,
            "battery_temperature": battery_temperature,
            "soc": soc if soc < 127 else None,
        }
