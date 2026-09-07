"""Tests for the diagnostics download."""

from __future__ import annotations

from homeassistant.core import HomeAssistant
from modbus_connection import IllegalDataAddressError
from modbus_connection.mock import MockModbusUnit
from pytest_homeassistant_custom_component.common import MockConfigEntry

from custom_components.schwoerer_lueftung.diagnostics import (
    async_get_config_entry_diagnostics,
)


async def setup_entry(hass: HomeAssistant, entry: MockConfigEntry) -> None:
    entry.add_to_hass(hass)
    assert await hass.config_entries.async_setup(entry.entry_id)
    await hass.async_block_till_done()


async def test_diagnostics_returns_the_raw_map(
    hass: HomeAssistant, mock_modbus, wgt_entry: MockConfigEntry
) -> None:
    await setup_entry(hass, wgt_entry)

    diagnostics = await async_get_config_entry_diagnostics(hass, wgt_entry)

    # Raw words, not decoded values: 215 rather than 21.5.
    assert diagnostics["registers"]["holding"][204] == 215
    assert "heating" in diagnostics["updated"]
    assert diagnostics["failed"] == {}


async def test_diagnostics_omits_the_host(
    hass: HomeAssistant, mock_modbus, wgt_entry: MockConfigEntry
) -> None:
    """The host identifies the user's network, so it stays out of the payload."""
    await setup_entry(hass, wgt_entry)

    diagnostics = await async_get_config_entry_diagnostics(hass, wgt_entry)

    assert "192.168.1.100" not in str(diagnostics)
    assert diagnostics["config"]["host_configured"] is True


async def test_a_failing_subsystem_still_yields_a_dump(
    hass: HomeAssistant,
    mock_modbus,
    unit: MockModbusUnit,
    wgt_entry: MockConfigEntry,
) -> None:
    """A dump is most wanted when something is refusing to answer."""
    await setup_entry(hass, wgt_entry)

    for address in (114, 115, 116):
        unit.fail_read(address, IllegalDataAddressError(2))
    await wgt_entry.runtime_data.async_refresh()

    diagnostics = await async_get_config_entry_diagnostics(hass, wgt_entry)

    assert "heating" in diagnostics["failed"]
    # The rest of the map still came back.
    assert diagnostics["registers"]["holding"][204] == 215
    assert 114 not in diagnostics["registers"]["holding"]
