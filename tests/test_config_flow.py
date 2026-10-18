"""Tests for the config flow."""

from __future__ import annotations

from homeassistant import config_entries
from homeassistant.const import CONF_HOST
from homeassistant.core import HomeAssistant
from homeassistant.data_entry_flow import FlowResultType
from homeassistant.helpers import device_registry as dr
from homeassistant.helpers import entity_registry as er
from modbus_connection import IllegalDataAddressError, ModbusConnectionError
from modbus_connection.mock import MockModbusUnit

from custom_components.schwoerer_lueftung.const import (
    CONF_DEVICE_TYPE,
    CONF_HAS_GROUND_HEAT_EXCHANGER,
    CONF_ROOMS,
    DEVICE_TYPE_WGT,
    DOMAIN,
)
from tests.conftest import make_entry

USER_INPUT = {
    CONF_HOST: "10.0.0.198",
    CONF_DEVICE_TYPE: DEVICE_TYPE_WGT,
    CONF_HAS_GROUND_HEAT_EXCHANGER: False,
    CONF_ROOMS: 3,
}


async def test_user_flow_creates_the_entry(hass: HomeAssistant, mock_modbus) -> None:
    result = await hass.config_entries.flow.async_init(
        DOMAIN, context={"source": config_entries.SOURCE_USER}
    )
    assert result["type"] is FlowResultType.FORM

    result = await hass.config_entries.flow.async_configure(
        result["flow_id"], USER_INPUT
    )
    await hass.async_block_till_done()

    assert result["type"] is FlowResultType.CREATE_ENTRY
    data = result["data"]
    assert data[CONF_HOST] == "10.0.0.198"
    assert data[CONF_DEVICE_TYPE] == DEVICE_TYPE_WGT
    assert [room["number"] for room in data[CONF_ROOMS]] == [1, 2, 3]


async def test_the_flow_asks_only_what_it_needs(
    hass: HomeAssistant, mock_modbus
) -> None:
    """No blanket "enable all sensors" question: it could never be changed
    afterwards, and Home Assistant's entity page does the job properly."""
    result = await hass.config_entries.flow.async_init(
        DOMAIN, context={"source": config_entries.SOURCE_USER}
    )

    keys = {str(key) for key in result["data_schema"].schema}
    assert keys == {
        CONF_HOST,
        CONF_DEVICE_TYPE,
        CONF_HAS_GROUND_HEAT_EXCHANGER,
        CONF_ROOMS,
    }


async def test_the_entry_carries_no_stale_option(
    hass: HomeAssistant, mock_modbus
) -> None:
    result = await hass.config_entries.flow.async_init(
        DOMAIN, context={"source": config_entries.SOURCE_USER}
    )
    result = await hass.config_entries.flow.async_configure(
        result["flow_id"], USER_INPUT
    )
    await hass.async_block_till_done()

    assert "enable_all_sensors_by_default" not in result["data"]


async def test_an_unreachable_device_is_reported(
    hass: HomeAssistant, mock_modbus, unit: MockModbusUnit
) -> None:
    unit.fail_requests(ModbusConnectionError("no route to host"))

    result = await hass.config_entries.flow.async_init(
        DOMAIN, context={"source": config_entries.SOURCE_USER}
    )
    result = await hass.config_entries.flow.async_configure(
        result["flow_id"], USER_INPUT
    )

    assert result["type"] is FlowResultType.FORM
    assert result["errors"] == {"base": "cannot_connect"}


async def test_a_firmware_without_optional_registers_can_be_added(
    hass: HomeAssistant, mock_modbus, unit: MockModbusUnit
) -> None:
    """The probe reads only the fan control block every firmware serves."""
    for address in range(142, 146):
        unit.fail_read(address, IllegalDataAddressError(2))

    result = await hass.config_entries.flow.async_init(
        DOMAIN, context={"source": config_entries.SOURCE_USER}
    )
    result = await hass.config_entries.flow.async_configure(
        result["flow_id"], USER_INPUT
    )
    await hass.async_block_till_done()

    assert result["type"] is FlowResultType.CREATE_ENTRY


async def test_a_refusing_device_is_told_apart_from_an_unreachable_one(
    hass: HomeAssistant, mock_modbus, unit: MockModbusUnit
) -> None:
    unit.fail_read(100, IllegalDataAddressError(2))

    result = await hass.config_entries.flow.async_init(
        DOMAIN, context={"source": config_entries.SOURCE_USER}
    )
    result = await hass.config_entries.flow.async_configure(
        result["flow_id"], USER_INPUT
    )

    assert result["type"] is FlowResultType.FORM
    assert result["errors"] == {"base": "device_refused"}


async def test_the_same_host_cannot_be_added_twice(
    hass: HomeAssistant, mock_modbus, wgt_entry
) -> None:
    wgt_entry.add_to_hass(hass)

    result = await hass.config_entries.flow.async_init(
        DOMAIN, context={"source": config_entries.SOURCE_USER}
    )
    result = await hass.config_entries.flow.async_configure(
        result["flow_id"], USER_INPUT | {CONF_HOST: wgt_entry.data[CONF_HOST]}
    )

    assert result["type"] is FlowResultType.ABORT
    assert result["reason"] == "already_configured"


async def _setup(hass: HomeAssistant, entry) -> None:
    entry.add_to_hass(hass)
    assert await hass.config_entries.async_setup(entry.entry_id)
    await hass.async_block_till_done()


async def test_reconfigure_moves_the_entry_to_a_new_host(
    hass: HomeAssistant, mock_modbus, wgt_entry
) -> None:
    """Entities and devices stay what they were; only the address changes."""
    await _setup(hass, wgt_entry)
    devices = dr.async_get(hass)
    entities = er.async_get(hass)
    device_ids = {
        d.id for d in dr.async_entries_for_config_entry(devices, wgt_entry.entry_id)
    }
    entity_ids = {
        e.entity_id
        for e in er.async_entries_for_config_entry(entities, wgt_entry.entry_id)
    }

    result = await wgt_entry.start_reconfigure_flow(hass)
    assert result["type"] is FlowResultType.FORM
    result = await hass.config_entries.flow.async_configure(
        result["flow_id"], {CONF_HOST: "192.168.1.200"}
    )
    await hass.async_block_till_done()

    assert result["type"] is FlowResultType.ABORT
    assert result["reason"] == "reconfigure_successful"
    assert wgt_entry.data[CONF_HOST] == "192.168.1.200"
    assert wgt_entry.unique_id == "192.168.1.200"

    moved = dr.async_entries_for_config_entry(devices, wgt_entry.entry_id)
    assert {d.id for d in moved} == device_ids
    assert {key for d in moved for _, key in d.identifiers} == {
        "192.168.1.200:502",
        "192.168.1.200:502#1",
        "192.168.1.200:502#2",
    }
    assert {
        e.entity_id
        for e in er.async_entries_for_config_entry(entities, wgt_entry.entry_id)
    } == entity_ids


async def test_reconfigure_refuses_a_host_another_entry_has(
    hass: HomeAssistant, mock_modbus, wgt_entry
) -> None:
    await _setup(hass, wgt_entry)
    other = make_entry()
    other.add_to_hass(hass)
    hass.config_entries.async_update_entry(
        other, unique_id="192.168.1.50", data={**other.data, CONF_HOST: "192.168.1.50"}
    )

    result = await wgt_entry.start_reconfigure_flow(hass)
    result = await hass.config_entries.flow.async_configure(
        result["flow_id"], {CONF_HOST: "192.168.1.50"}
    )

    assert result["type"] is FlowResultType.ABORT
    assert result["reason"] == "already_configured"
    assert wgt_entry.data[CONF_HOST] == "192.168.1.100"


async def test_reconfigure_reports_an_unreachable_host(
    hass: HomeAssistant, mock_modbus, unit: MockModbusUnit, wgt_entry
) -> None:
    await _setup(hass, wgt_entry)
    unit.fail_requests(ModbusConnectionError("no route to host"))

    result = await wgt_entry.start_reconfigure_flow(hass)
    result = await hass.config_entries.flow.async_configure(
        result["flow_id"], {CONF_HOST: "192.168.1.200"}
    )

    assert result["type"] is FlowResultType.FORM
    assert result["errors"] == {"base": "cannot_connect"}
    assert wgt_entry.data[CONF_HOST] == "192.168.1.100"
