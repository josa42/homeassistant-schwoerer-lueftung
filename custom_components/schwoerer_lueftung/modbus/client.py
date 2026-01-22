"""Modbus TCP client for Schwörer Lüftung."""
from __future__ import annotations

import logging
from itertools import groupby
from typing import Any, Callable

from pymodbus.client import ModbusTcpClient
from .registers import REG_KEYS, REG_TO_TRANSFORM

_LOGGER = logging.getLogger(__name__)


class ModbusClient:
    """Modbus TCP client for WRG device."""

    def __init__(self, host: str, port: int, slave_id: int, device_type: str = "wgt") -> None:
        """Initialize the Modbus client."""
        self.host = host
        self.port = port
        self.slave_id = slave_id
        self.device_type = device_type
        self._client = ModbusTcpClient(
            host=host,
            port=port,
            timeout=5,
            retries=3,
        )
        self._subscriptions: dict[int, tuple[str, None | Callable]] = {}

    ############################################################################
    # Connection management

    def connect(self) -> bool:
        """Connect to the Modbus device."""
        return self._client.connect()

    def disconnect(self) -> None:
        """Disconnect from the Modbus device."""
        self._client.close()

    def is_connected(self) -> bool:
        """Check if connected to the Modbus device."""
        return self._client.is_socket_open()

    ############################################################################
    # subscription management

    def is_subscribed(self, register: int) -> bool:
        """Check if a register is subscribed."""
        return register in self._subscriptions

    def subscribe(self, register: int) -> None:
        """Subscribe to a register for reading."""
        key = REG_KEYS.get(register)
        if key is not None:
            self._subscriptions[register] = (key, REG_TO_TRANSFORM.get(register))
        else:
            _LOGGER.error("Attempted to subscribe to unknown register: %s", register)

    ############################################################################
    # Read/Write operations

    def read_registers(self, address: int, count: int) -> list[int] | None:
        try:
            result = self._client.read_holding_registers(address=address, count=count)
            if result.isError():
                _LOGGER.error("Error reading registers at %s: %s", address, result)
                return None
            _LOGGER.debug("-> Read registers at %s [len: %d]: %s", address, count, result.registers)
            return result.registers
        except Exception as err:
            _LOGGER.error("Error reading registers at %s: %s", address, err)
            return None

    def write_register(self, address: int, value: int) -> bool:
        try:
            # Device requires Write Multiple Registers (16), not Write Single Register (06)
            result = self._client.write_registers(address=address, values=[value])
            if result.isError():
                _LOGGER.error("Error writing register at %s: %s", address, result)
                return False
            return True
        except Exception as err:
            _LOGGER.error("Error writing register at %s: %s", address, err)
            return False

    ############################################################################
    # Update data

    def read_data(self) -> dict[str, Any]:
        """Read all relevant data from the device."""
        data = {}

        if len(self._subscriptions) == 0:
            return data

        groups = self._get_grouped_subscriptions()

        _LOGGER.debug("Reading data in %d groups: %s", len(groups), groups)

        for group in groups:
            registers = list(group.keys())

            values = self.read_registers(registers[0], len(registers))
            if values is None:
                continue

            for i, address in enumerate(registers):
                try:
                    key = REG_KEYS.get(address)
                    transform = REG_TO_TRANSFORM.get(address)

                    if key is None:
                        _LOGGER.error("Register %d not in REG_KEYS", address)
                        continue

                    data[key] = transform(values[i]) if transform else values[i]

                    if key != REG_KEYS.get(address):
                        _LOGGER.error(
                            "Register %d key mismatch: expected %s, got %s", address, REG_KEYS.get(address), key
                        )
                except Exception as err:
                    _LOGGER.error("Error transforming register %d value %s: %s", address, values[i], err)

        return data

    def _get_grouped_subscriptions(self) -> list[dict[int, tuple[str, Callable | None]]]:
        """Group consecutive register addresses together for efficient reading."""
        sorted_keys = sorted(self._subscriptions.keys())
        groups = []

        for _, group_keys in groupby(enumerate(sorted_keys), key=lambda x: x[0] - x[1]):
            group_dict = {key: self._subscriptions[key] for _, key in group_keys}

            # Split groups longer than 125
            if len(group_dict) > 125:
                keys_list = sorted(group_dict.keys())
                for i in range(0, len(keys_list), 125):
                    chunk = {k: group_dict[k] for k in keys_list[i:i+125]}
                    groups.append(chunk)
            else:
                groups.append(group_dict)

        return groups


