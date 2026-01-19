"""Modbus TCP client for BIC WRG."""
from __future__ import annotations

import logging
from typing import Any

from pymodbus.client import ModbusTcpClient
from pymodbus.exceptions import ModbusException

_LOGGER = logging.getLogger(__name__)

# Register addresses
# Betriebsart (Operation Mode)
REG_OPERATION_MODE = 100
# Manuelle Luftstufe (Manual Fan Speed)
REG_FAN_SPEED = 101
# Aktuelle Luftstufe (Current Fan Level)
REG_CURRENT_FAN_LEVEL = 102

# Operation mode values
# Betriebsart: 0=Aus, 1=Handbetrieb, 2=Winterbetrieb, 3=Sommerbetrieb, 4=Sommer Abluft
OPERATION_MODE_OFF = 0
OPERATION_MODE_MANUAL = 1
OPERATION_MODE_WINTER = 2
OPERATION_MODE_SUMMER = 3
OPERATION_MODE_SUMMER_EXHAUST = 4

# Fan speed values
# Manuelle Luftstufe: 0=Aus, 1=Stufe 1, 2=Stufe 2, 3=Stufe 3, 4=Stufe 4, 5=Automatik, 6=Linearbetrieb
FAN_SPEED_OFF = 0
FAN_SPEED_LEVEL_1 = 1
FAN_SPEED_LEVEL_2 = 2
FAN_SPEED_LEVEL_3 = 3
FAN_SPEED_LEVEL_4 = 4
FAN_SPEED_AUTO = 5
FAN_SPEED_LINEAR = 6

# Current fan level values
# Aktuelle Luftstufe: 0=Aus, 1=Stufe 1, 2=Stufe 2, 3=Stufe 3, 4=Stufe 4
CURRENT_FAN_LEVEL_OFF = 0
CURRENT_FAN_LEVEL_1 = 1
CURRENT_FAN_LEVEL_2 = 2
CURRENT_FAN_LEVEL_3 = 3
CURRENT_FAN_LEVEL_4 = 4


class BicWrgModbusClient:
    """Modbus TCP client for WRG device."""

    def __init__(self, host: str, port: int, slave_id: int) -> None:
        """Initialize the Modbus client."""
        self.host = host
        self.port = port
        self.slave_id = slave_id
        self._client = ModbusTcpClient(
            host=host,
            port=port,
            timeout=5,
            retries=3,
        )

    def connect(self) -> bool:
        """Connect to the Modbus device."""
        return self._client.connect()

    def disconnect(self) -> None:
        """Disconnect from the Modbus device."""
        self._client.close()

    def is_connected(self) -> bool:
        """Check if connected to the Modbus device."""
        return self._client.is_socket_open()

    def read_holding_registers(
        self, address: int, count: int = 1
    ) -> list[int] | None:
        """Read holding registers from the device."""
        try:
            result = self._client.read_holding_registers(
                address=address, count=count, slave=self.slave_id
            )
            if result.isError():
                _LOGGER.error("Error reading registers at %s: %s", address, result)
                return None
            return result.registers
        except TypeError:
            # Try without slave parameter (newer pymodbus API)
            try:
                result = self._client.read_holding_registers(
                    address=address, count=count
                )
                if result.isError():
                    _LOGGER.error("Error reading registers at %s: %s", address, result)
                    return None
                return result.registers
            except Exception as err:
                _LOGGER.error("Error reading registers at %s: %s", address, err)
                return None
        except ModbusException as err:
            _LOGGER.error("Modbus exception reading registers: %s", err)
            return None
        except Exception as err:
            _LOGGER.error("Unexpected error reading registers at %s: %s", address, err)
            return None

    def write_register(self, address: int, value: int) -> bool:
        """Write a single register to the device using Write Multiple Registers (16)."""
        try:
            # Device requires Write Multiple Registers (16), not Write Single Register (06)
            result = self._client.write_registers(
                address=address, values=[value], slave=self.slave_id
            )
            if result.isError():
                _LOGGER.error("Error writing register at %s: %s", address, result)
                return False
            return True
        except TypeError:
            # Try without slave parameter (newer pymodbus API)
            try:
                result = self._client.write_registers(
                    address=address, values=[value]
                )
                if result.isError():
                    _LOGGER.error("Error writing register at %s: %s", address, result)
                    return False
                return True
            except Exception as err:
                _LOGGER.error("Error writing register at %s: %s", address, err)
                return False
        except ModbusException as err:
            _LOGGER.error("Modbus exception writing register: %s", err)
            return False
        except Exception as err:
            _LOGGER.error("Unexpected error writing register at %s: %s", address, err)
            return False

    def read_operation_mode(self) -> int | None:
        """Read operation mode (Betriebsart)."""
        registers = self.read_holding_registers(REG_OPERATION_MODE, 1)
        if registers:
            return registers[0]
        return None

    def write_operation_mode(self, mode: int) -> bool:
        """Write operation mode (Betriebsart)."""
        return self.write_register(REG_OPERATION_MODE, mode)

    def read_fan_speed(self) -> int | None:
        """Read manual fan speed (Manuelle Luftstufe)."""
        registers = self.read_holding_registers(REG_FAN_SPEED, 1)
        if registers:
            return registers[0]
        return None

    def write_fan_speed(self, speed: int) -> bool:
        """Write manual fan speed (Manuelle Luftstufe)."""
        return self.write_register(REG_FAN_SPEED, speed)

    def read_current_fan_level(self) -> int | None:
        """Read current fan level (Aktuelle Luftstufe)."""
        registers = self.read_holding_registers(REG_CURRENT_FAN_LEVEL, 1)
        if registers:
            return registers[0]
        return None

    def read_data(self) -> dict[str, Any]:
        """Read all relevant data from the device."""
        data = {}
        
        # Read operation mode (Betriebsart)
        operation_mode = self.read_operation_mode()
        if operation_mode is not None:
            data["operation_mode"] = operation_mode
        
        # Read fan speed (Manuelle Luftstufe)
        fan_speed = self.read_fan_speed()
        if fan_speed is not None:
            data["fan_speed"] = fan_speed
        
        # Read current fan level (Aktuelle Luftstufe)
        current_fan_level = self.read_current_fan_level()
        if current_fan_level is not None:
            data["current_fan_level"] = current_fan_level
        
        return data
