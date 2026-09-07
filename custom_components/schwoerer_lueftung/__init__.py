from __future__ import annotations

from homeassistant.components.modbus import async_get_unit
from homeassistant.const import CONF_HOST, Platform
from homeassistant.core import HomeAssistant
from modbus_connection import ModbusTcpParams

from .const import (
    CONF_DEVICE_TYPE,
    CONF_HAS_GROUND_HEAT_EXCHANGER,
    CONF_ROOMS,
    DEFAULT_DEVICE_TYPE,
    DEFAULT_PORT,
    DEFAULT_UNIT_ID,
    DEVICE_TYPE_WGT,
)
from .coordinator import Coordinator, SchwoererConfigEntry
from .device import SchwoererDevice

PLATFORMS: list[Platform] = [
    Platform.BINARY_SENSOR,
    Platform.CLIMATE,
    Platform.NUMBER,
    Platform.SELECT,
    Platform.SENSOR,
    Platform.SWITCH,
]


async def async_setup_entry(hass: HomeAssistant, entry: SchwoererConfigEntry) -> bool:
    # The modbus integration owns the connection and shares it with anything
    # else talking to this device. Asking for a unit does no I/O, and there is
    # no teardown to register: the connection closes when the last entry
    # holding a unit on it unloads.
    unit = async_get_unit(
        hass,
        entry,
        ModbusTcpParams(host=entry.data[CONF_HOST], port=DEFAULT_PORT),
        DEFAULT_UNIT_ID,
    )

    # Which sub-systems the device has is settled by the config entry, so the
    # ones it lacks are never constructed and their registers never read.
    device = SchwoererDevice(
        unit,
        has_heating=entry.data.get(CONF_DEVICE_TYPE, DEFAULT_DEVICE_TYPE)
        == DEVICE_TYPE_WGT,
        has_ground_heat_exchanger=entry.data.get(CONF_HAS_GROUND_HEAT_EXCHANGER, False),
        room_numbers=[room["number"] for room in entry.data.get(CONF_ROOMS, [])],
    )

    coordinator = Coordinator(hass, entry, device)

    # The first read establishes the link. If the device is unreachable it
    # fails here and Home Assistant retries setup for us.
    await coordinator.async_config_entry_first_refresh()
    entry.runtime_data = coordinator

    # Register the main device so the room devices can be attached to it.
    coordinator.register_device()

    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)

    return True


async def async_unload_entry(hass: HomeAssistant, entry: SchwoererConfigEntry) -> bool:
    return await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
