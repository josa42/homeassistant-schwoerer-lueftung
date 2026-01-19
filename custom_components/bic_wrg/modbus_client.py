"""Modbus TCP client for BIC WRG."""
from __future__ import annotations

import logging
from typing import Any

from pymodbus.client import ModbusTcpClient
from pymodbus.exceptions import ModbusException

_LOGGER = logging.getLogger(__name__)


class BicWrgModbusClient:
    """Modbus TCP client for WRG device."""

    def __init__(self, host: str, port: int, slave_id: int) -> None:
        """Initialize the Modbus client."""
        self.host = host
        self.port = port
        self.slave_id = slave_id
        self._client = ModbusTcpClient(host=host, port=port, timeout=5)

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
        except ModbusException as err:
            _LOGGER.error("Modbus exception reading registers: %s", err)
            return None

    def write_register(self, address: int, value: int) -> bool:
        """Write a single register to the device."""
        try:
            result = self._client.write_register(
                address=address, value=value, slave=self.slave_id
            )
            if result.isError():
                _LOGGER.error("Error writing register at %s: %s", address, result)
                return False
            return True
        except ModbusException as err:
            _LOGGER.error("Modbus exception writing register: %s", err)
            return False

    def read_data(self) -> dict[str, Any]:
        """Read all relevant data from the device."""
        # TODO: Define actual register mappings for WRG 134-BP-HK
        # This is a placeholder structure
        data = {}
        
        # Example: Read temperature registers (adjust addresses as needed)
        # registers = self.read_holding_registers(address=0, count=10)
        # if registers:
        #     data["supply_temp"] = registers[0] / 10.0
        #     data["extract_temp"] = registers[1] / 10.0
        #     data["outdoor_temp"] = registers[2] / 10.0
        
        return data
