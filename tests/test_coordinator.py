"""Tests for the coordinator's polling and error mapping."""

from __future__ import annotations

import pytest
from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import UpdateFailed
from modbus_connection import IllegalDataAddressError, ModbusConnectionError
from modbus_connection.mock import MockModbusUnit
from pytest_homeassistant_custom_component.common import MockConfigEntry


async def setup_entry(hass: HomeAssistant, entry: MockConfigEntry) -> MockConfigEntry:
    entry.add_to_hass(hass)
    assert await hass.config_entries.async_setup(entry.entry_id)
    await hass.async_block_till_done()
    return entry


async def test_data_is_the_update_report(
    hass: HomeAssistant, mock_modbus, wgt_entry: MockConfigEntry
) -> None:
    """Every sub-system a WGT with a ground heat exchanger has answers."""
    await setup_entry(hass, wgt_entry)

    report = wgt_entry.runtime_data.data
    assert set(report.updated) == {
        "ventilation",
        "temperatures",
        "alarms",
        "operating_hours",
        "heating",
        "ground_heat_exchanger",
        "rooms",
    }
    assert report.failed == {}


async def test_a_wrt_reports_only_what_it_has(
    hass: HomeAssistant, mock_modbus, wrt_entry: MockConfigEntry
) -> None:
    await setup_entry(hass, wrt_entry)

    report = wrt_entry.runtime_data.data
    assert "heating" not in report.updated
    assert "ground_heat_exchanger" not in report.updated
    assert report.failed == {}


async def test_a_refused_subsystem_is_reported_not_raised(
    hass: HomeAssistant,
    mock_modbus,
    unit: MockModbusUnit,
    wgt_entry: MockConfigEntry,
) -> None:
    """One failing block must not fail the poll."""
    await setup_entry(hass, wgt_entry)

    for address in (114, 115, 116):
        unit.fail_read(address, IllegalDataAddressError(2))

    report = await wgt_entry.runtime_data._async_update_data()

    assert "heating" in report.failed
    assert "ventilation" in report.updated


async def test_a_dead_link_fails_the_update(
    hass: HomeAssistant,
    mock_modbus,
    unit: MockModbusUnit,
    wgt_entry: MockConfigEntry,
) -> None:
    """A dropped connection surfaces as UpdateFailed, not as a reload."""
    await setup_entry(hass, wgt_entry)
    coordinator = wgt_entry.runtime_data

    unit.fail_requests(ModbusConnectionError("connection reset"))

    with pytest.raises(UpdateFailed):
        await coordinator._async_update_data()


async def test_writing_a_field_refreshes(
    hass: HomeAssistant,
    mock_modbus,
    unit: MockModbusUnit,
    wgt_entry: MockConfigEntry,
) -> None:
    await setup_entry(hass, wgt_entry)
    coordinator = wgt_entry.runtime_data

    await coordinator.async_write(coordinator.device.ventilation, "fan_speed", 3)
    await hass.async_block_till_done()

    assert unit.holding[101] == 3
    assert coordinator.device.ventilation.fan_speed == 3
