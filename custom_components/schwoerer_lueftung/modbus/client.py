"""Modbus TCP client for Schwörer Lüftung."""

from __future__ import annotations

import logging
from itertools import groupby
from typing import Any

from pymodbus.client import ModbusTcpClient

from .registers import REG_KEYS

_LOGGER = logging.getLogger(__name__)


class ModbusClient:
    _subscriptions: set[int] = set()

    def __init__(self, host: str, port: int) -> None:
        """Initialize the Modbus client."""
        self.host = host
        self.port = port
        self._client = ModbusTcpClient(
            host=host,
            port=port,
            timeout=5,
            retries=3,
        )

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
        if not self.is_subscribed(register):
            if REG_KEYS.get(register) is not None:
                self._subscriptions.add(register)
            else:
                _LOGGER.error(
                    "Attempted to subscribe to unknown register: %s", register
                )

    ############################################################################
    # Read/Write operations

    def read_registers(self, address: int, count: int) -> list[int] | None:
        try:
            result = self._client.read_holding_registers(address=address, count=count)
            if result.isError():
                _LOGGER.error("Error reading registers at %s: %s", address, result)
                return None
            _LOGGER.debug(
                "Read registers at %d - %d: %s",
                address,
                address + count - 1,
                result.registers,
            )
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

        for registers in groups:
            values = self.read_registers(registers[0], len(registers))
            if values is None:
                continue

            for i, address in enumerate(registers):
                try:
                    key = REG_KEYS.get(address)

                    if key is None:
                        _LOGGER.error("Register %d not in REG_KEYS", address)
                        continue

                    data[key] = values[i]

                except Exception as err:
                    _LOGGER.error(
                        "Error processing register %d value %s: %s",
                        address,
                        values[i],
                        err,
                    )

        return data

    def _get_grouped_subscriptions(self) -> list[list[int]]:
        """Group consecutive register addresses together for efficient reading."""
        groups = []

        for _, groupped_subscriptions in groupby(
            enumerate(sorted(self._subscriptions)), key=lambda x: x[0] - x[1]
        ):
            group = [x for _, x in list(groupped_subscriptions)]

            # Split groups longer than 125
            groups.extend(group[i : i + 125] for i in range(0, len(group), 125))

        return groups
