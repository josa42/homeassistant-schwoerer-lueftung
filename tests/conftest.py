"""Fixtures for tests."""

from __future__ import annotations

from contextlib import asynccontextmanager
from unittest.mock import patch

import pytest
from homeassistant.const import CONF_HOST
from modbus_connection.mock import MockModbusConnection, MockModbusUnit
from pytest_homeassistant_custom_component.common import MockConfigEntry

from custom_components.schwoerer_lueftung.const import (
    CONF_DEVICE_TYPE,
    CONF_ENABLE_ALL_SENSORS_BY_DEFAULT,
    CONF_HAS_GROUND_HEAT_EXCHANGER,
    CONF_ROOMS,
    DEVICE_TYPE_WGT,
    DEVICE_TYPE_WRT,
    DOMAIN,
)

# Every address any component declares a field at, with a value that decodes
# to something plausible. Temperatures are tenths of a degree, so 215 is 21.5.
SEEDED_REGISTERS: dict[int, int] = {
    # Ventilation
    100: 2,
    101: 5,
    102: 3,
    103: 60,
    104: 0,
    110: 2,
    111: 0,
    112: 0,
    117: 2,
    118: 2,
    123: 0,
    131: 1,
    133: 0,
    140: 2,
    141: 1,
    142: 55,
    143: 55,
    144: 1200,
    145: 1150,
    # Heating
    114: 5,
    116: 1,
    201: 15,
    202: 180,
    203: 205,
    206: 35,
    207: 420,
    230: 1,
    231: 1,
    232: 0,
    234: 1,
    # Ground heat exchanger
    121: 1,
    # Undocumented: T9, and the device clock at 620-625
    208: 259,
    620: 2026,
    621: 9,
    622: 7,
    623: 12,
    624: 21,
    625: 32,
    # Temperatures
    200: 95,
    204: 215,
    205: 190,
    209: 78,
    # Alarms
    240: 0,
    242: 0,
    243: 0,
    244: 0,
    245: 0,
    246: 0,
    247: 0,
    248: 0,
    250: 0,
    251: 0,
    252: 0,
    253: 0,
    254: 0,
    263: 120,
    265: 45,
    # Operating hours
    800: 12000,
    801: 3000,
    802: 4000,
    803: 2500,
    804: 500,
    805: 6000,
    806: 900,
    809: 300,
    810: 150,
    813: 800,
}

# Rooms 1-17: current, target, base temperature, then the three 0/1 flags.
for _offset in range(17):
    SEEDED_REGISTERS[360 + _offset] = 210 + _offset
    SEEDED_REGISTERS[400 + _offset] = 220
    SEEDED_REGISTERS[420 + _offset] = 205
    SEEDED_REGISTERS[440 + _offset] = 1
    SEEDED_REGISTERS[460 + _offset] = 0
    SEEDED_REGISTERS[500 + _offset] = 1


@pytest.fixture(autouse=True)
def auto_enable_custom_integrations(enable_custom_integrations):
    """Enable custom integrations for testing."""
    yield


@pytest.fixture
def unit() -> MockModbusUnit:
    """A mock Modbus unit seeded with a full, plausible register map."""
    mock_unit = MockModbusConnection().for_unit(1)
    for address, value in SEEDED_REGISTERS.items():
        mock_unit.holding[address] = value
    return mock_unit


@pytest.fixture
def mock_modbus(unit: MockModbusUnit):
    """Hand the mock unit out instead of asking the modbus integration.

    Both entry points are patched: `async_get_unit` for setup and
    `async_get_temporary_unit` for the config flow's probe.
    """

    @asynccontextmanager
    async def temporary_unit(*args, **kwargs):
        yield unit

    with (
        patch(
            "custom_components.schwoerer_lueftung.async_get_unit", return_value=unit
        ) as get_unit,
        patch(
            "custom_components.schwoerer_lueftung.config_flow.async_get_temporary_unit",
            temporary_unit,
        ),
    ):
        yield get_unit


def make_entry(
    *,
    device_type: str = DEVICE_TYPE_WGT,
    ground_heat_exchanger: bool = True,
    rooms: int = 2,
    enable_all: bool = False,
) -> MockConfigEntry:
    """A config entry shaped the way the config flow writes one."""
    return MockConfigEntry(
        domain=DOMAIN,
        data={
            CONF_HOST: "192.168.1.100",
            CONF_DEVICE_TYPE: device_type,
            CONF_HAS_GROUND_HEAT_EXCHANGER: ground_heat_exchanger,
            CONF_ENABLE_ALL_SENSORS_BY_DEFAULT: enable_all,
            CONF_ROOMS: [
                {"number": n, "name": f"Room {n}"} for n in range(1, rooms + 1)
            ],
        },
    )


@pytest.fixture
def wgt_entry() -> MockConfigEntry:
    """A WGT with a ground heat exchanger and two rooms."""
    return make_entry()


@pytest.fixture
def wrt_entry() -> MockConfigEntry:
    """A WRT with neither heating nor a ground heat exchanger."""
    return make_entry(device_type=DEVICE_TYPE_WRT, ground_heat_exchanger=False, rooms=2)


@pytest.fixture
def wgt_entry_all_enabled() -> MockConfigEntry:
    """A WGT with the config flow's "enable all sensors" option turned on."""
    return make_entry(enable_all=True)
