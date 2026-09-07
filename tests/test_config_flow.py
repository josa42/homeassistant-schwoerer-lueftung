"""Tests for the config flow."""

from __future__ import annotations

from homeassistant import config_entries
from homeassistant.const import CONF_HOST
from homeassistant.core import HomeAssistant
from homeassistant.data_entry_flow import FlowResultType
from modbus_connection import ModbusConnectionError
from modbus_connection.mock import MockModbusUnit

from custom_components.schwoerer_lueftung.const import (
    CONF_DEVICE_TYPE,
    CONF_HAS_GROUND_HEAT_EXCHANGER,
    CONF_ROOMS,
    DEVICE_TYPE_WGT,
    DOMAIN,
)

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
