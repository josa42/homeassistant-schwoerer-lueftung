"""Modbus TCP client for BIC WRG."""
from __future__ import annotations

import logging
from itertools import groupby
from typing import Any, Callable

from pymodbus.client import ModbusTcpClient
from pymodbus.exceptions import ModbusException

from .registers import (
    LINEAR_FAN_POWER_MAX,
    LINEAR_FAN_POWER_MIN,
    REG_AUXILIARY_HEATING_ENABLE,
    REG_FAN_SPEED,
    REG_HEATING_COOLING_FUNCTION,
    REG_HEAT_PUMP_COOLING_ENABLE,
    REG_HEAT_PUMP_HEATING_ENABLE,
    REG_KEYS,
    REG_LINEAR_FAN_POWER,
    REG_OPERATION_MODE,
    REG_SHOCK_VENTILATION,
    REG_TO_TRANSFORM,
)

_LOGGER = logging.getLogger(__name__)


def group_consecutive(d: dict[int, tuple[str, Callable | None]]) -> list[dict[int, tuple[str, Callable | None]]]:
    """Group consecutive register addresses together for efficient reading."""
    sorted_keys = sorted(d.keys())
    groups = []

    for _, group_keys in groupby(enumerate(sorted_keys), key=lambda x: x[0] - x[1]):
        group_dict = {key: d[key] for _, key in group_keys}

        # Split groups longer than 125
        if len(group_dict) > 125:
            keys_list = sorted(group_dict.keys())
            for i in range(0, len(keys_list), 125):
                chunk = {k: group_dict[k] for k in keys_list[i:i+125]}
                groups.append(chunk)
        else:
            groups.append(group_dict)

    return groups


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

    def connect(self) -> bool:
        """Connect to the Modbus device."""
        return self._client.connect()

    def disconnect(self) -> None:
        """Disconnect from the Modbus device."""
        self._client.close()

    def is_connected(self) -> bool:
        """Check if connected to the Modbus device."""
        return self._client.is_socket_open()

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

    def read_registers(
        self, address: int, count: int
    ) -> list[int] | None:
        """Read holding registers from the device."""
        try:
            result = self._client.read_holding_registers(address=address, count=count)
            if result.isError():
                _LOGGER.error("Error reading registers at %s: %s", address, result)
                return None
            _LOGGER.info("-> Read registers at %s [len: %d]: %s", address, count, result.registers)
            return result.registers
        except ModbusException as err:
            _LOGGER.error("Modbus exception reading registers: %s", err)
            return None
        except Exception as err:
            _LOGGER.error("Unexpected error reading registers at %s: %s", address, err)
            return None

    def read_register(
        self, address: int
    ) -> int | None:
        """Read a single holding register from the device."""
        try:
            result = self._client.read_holding_registers(address=address, count=1)
            if result.isError():
                _LOGGER.error("Error reading register at %s: %s", address, result)
                return None
            return result.registers[0] if result.registers else None
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
                address=address, values=[value]
            )
            if result.isError():
                _LOGGER.error("Error writing register at %s: %s", address, result)
                return False
            return True
        except ModbusException as err:
            _LOGGER.error("Modbus exception writing register: %s", err)
            return False
        except Exception as err:
            _LOGGER.error("Unexpected error writing register at %s: %s", address, err)
            return False

    def write_operation_mode(self, mode: int) -> bool:
        """Write operation mode (Betriebsart)."""
        return self.write_register(REG_OPERATION_MODE, mode)

    def write_room_target_temperature(self, room_number: int, temperature: float) -> bool:
        """Write room target temperature (Soll Temp Raum)."""
        # Rooms 1-17 use registers 400-416
        # Temperature range: 10-30°C, stored as value * 10
        register = 400 + room_number - 1
        value = int(temperature * 10)
        return self.write_register(register, value)

    def write_room_heating_enable(self, room_number: int, enabled: int) -> bool:
        """Write room heating enable (Zusatzheizung Freigabe Raum)."""
        # Rooms 1-17 have heating enable (registers 440-456)
        if room_number < 1 or room_number > 17:
            return False
        register = 440 + room_number - 1
        return self.write_register(register, enabled)

    def write_fan_speed(self, speed: int) -> bool:
        """Write manual fan speed (Manuelle Luftstufe)."""
        return self.write_register(REG_FAN_SPEED, speed)

    def write_linear_fan_power(self, power: int) -> bool:
        """Write manual linear fan power (Manuelle Lineare Luftleistung)."""
        # Validate range 30-100
        if power < LINEAR_FAN_POWER_MIN or power > LINEAR_FAN_POWER_MAX:
            _LOGGER.error(
                "Linear fan power %d out of range (%d-%d)",
                power,
                LINEAR_FAN_POWER_MIN,
                LINEAR_FAN_POWER_MAX,
            )
            return False
        return self.write_register(REG_LINEAR_FAN_POWER, power)

    def write_shock_ventilation(self, active: int) -> bool:
        """Write shock ventilation (Stoßlüftung)."""
        return self.write_register(REG_SHOCK_VENTILATION, active)

    def write_heating_cooling_function(self, mode: int) -> bool:
        """Write heating/cooling function (Heiz-Kühlfunktion)."""
        return self.write_register(REG_HEATING_COOLING_FUNCTION, mode)

    def write_heat_pump_heating_enable(self, enabled: int) -> bool:
        """Write heat pump heating enable (Wärmepumpe Heizen)."""
        return self.write_register(REG_HEAT_PUMP_HEATING_ENABLE, enabled)

    def write_heat_pump_cooling_enable(self, enabled: int) -> bool:
        """Write heat pump cooling enable (Wärmepumpe Kühlen)."""
        return self.write_register(REG_HEAT_PUMP_COOLING_ENABLE, enabled)

    def write_auxiliary_heating_enable(self, enabled: int) -> bool:
        """Write auxiliary heating enable (Zusatzheizung Haus)."""
        return self.write_register(REG_AUXILIARY_HEATING_ENABLE, enabled)

    def write_room_base_temperature(self, room_number: int, temperature: float) -> bool:
        """Write room base temperature (Grundtemperatur Raum)."""
        # Rooms 1-17 use registers 420-436
        # Temperature range: 10-30°C, stored as value * 10
        register = 420 + room_number - 1
        value = int(temperature * 10)
        return self.write_register(register, value)

    def read_data(self) -> dict[str, Any]:
        """Read all relevant data from the device."""
        data = {}

        if len(self._subscriptions) == 0:
            return data

        groups = group_consecutive(self._subscriptions)

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
                        _LOGGER.error("Register %d key mismatch: expected %s, got %s", address, REG_KEYS.get(address), key)
                except Exception as err:
                    _LOGGER.error("Error transforming register %d value %s: %s", address, values[i], err)

        return data
