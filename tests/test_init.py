"""Test the Schwörer Lüftung integration setup and teardown."""

from __future__ import annotations

from homeassistant.config_entries import ConfigEntryState
from homeassistant.const import CONF_HOST
from homeassistant.core import HomeAssistant
from modbus_connection import ModbusConnectionError, ModbusTcpParams
from modbus_connection.mock import MockModbusUnit
from pytest_homeassistant_custom_component.common import MockConfigEntry

from custom_components.schwoerer_lueftung.const import DEFAULT_PORT, DEFAULT_UNIT_ID


async def test_setup_entry(
    hass: HomeAssistant, mock_modbus, wgt_entry: MockConfigEntry
) -> None:
    """The entry loads and the coordinator lands on runtime_data."""
    wgt_entry.add_to_hass(hass)

    assert await hass.config_entries.async_setup(wgt_entry.entry_id)
    await hass.async_block_till_done()

    assert wgt_entry.state is ConfigEntryState.LOADED
    assert wgt_entry.runtime_data.data.updated


async def test_setup_asks_modbus_for_the_unit(
    hass: HomeAssistant, mock_modbus, wgt_entry: MockConfigEntry
) -> None:
    """We do not open our own socket; we ask for a unit on a shared one."""
    wgt_entry.add_to_hass(hass)

    assert await hass.config_entries.async_setup(wgt_entry.entry_id)
    await hass.async_block_till_done()

    mock_modbus.assert_called_once()
    _hass, entry, params, unit_id = mock_modbus.call_args.args
    assert entry is wgt_entry
    assert params == ModbusTcpParams(host=wgt_entry.data[CONF_HOST], port=DEFAULT_PORT)
    assert unit_id == DEFAULT_UNIT_ID


async def test_unload_entry(
    hass: HomeAssistant, mock_modbus, wgt_entry: MockConfigEntry
) -> None:
    """Unloading tears the platforms down; the connection is modbus's to close."""
    wgt_entry.add_to_hass(hass)

    assert await hass.config_entries.async_setup(wgt_entry.entry_id)
    await hass.async_block_till_done()

    assert await hass.config_entries.async_unload(wgt_entry.entry_id)
    await hass.async_block_till_done()

    assert wgt_entry.state is ConfigEntryState.NOT_LOADED


async def test_setup_retries_when_the_device_is_unreachable(
    hass: HomeAssistant, mock_modbus, unit: MockModbusUnit, wgt_entry: MockConfigEntry
) -> None:
    """The first read establishes the link, so a dead device means a retry."""
    unit.fail_requests(ModbusConnectionError("no route to host"))
    wgt_entry.add_to_hass(hass)

    assert not await hass.config_entries.async_setup(wgt_entry.entry_id)
    await hass.async_block_till_done()

    assert wgt_entry.state is ConfigEntryState.SETUP_RETRY
