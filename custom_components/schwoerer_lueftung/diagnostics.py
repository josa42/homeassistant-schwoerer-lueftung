"""Diagnostics support for Schwörer Lüftung.

The payload is the raw register map: every address the integration reads, with
the word the device returned, undecoded. That makes an issue report show
exactly what the hardware said rather than what we made of it — and the dump
replays straight into modbus-connection's mock backend with ``load_raw()``, so
a report from a configuration we cannot test here can become a regression test
with no hardware.
"""

from __future__ import annotations

from typing import Any

from homeassistant.const import CONF_HOST
from homeassistant.core import HomeAssistant
from modbus_connection import ModbusError

from .const import CONF_DEVICE_TYPE, CONF_HAS_GROUND_HEAT_EXCHANGER, CONF_ROOMS
from .coordinator import SchwoererConfigEntry


async def async_get_config_entry_diagnostics(
    hass: HomeAssistant, entry: SchwoererConfigEntry
) -> dict[str, Any]:
    """Return the register map and the last poll's outcome."""
    coordinator = entry.runtime_data
    report = coordinator.data

    diagnostics: dict[str, Any] = {
        "config": {
            # The host is the one piece of the entry that identifies the user's
            # network, so it is left out.
            CONF_DEVICE_TYPE: entry.data.get(CONF_DEVICE_TYPE),
            CONF_HAS_GROUND_HEAT_EXCHANGER: entry.data.get(
                CONF_HAS_GROUND_HEAT_EXCHANGER
            ),
            "room_count": len(entry.data.get(CONF_ROOMS, [])),
            "host_configured": CONF_HOST in entry.data,
        },
        "updated": report.updated,
        "failed": {name: str(err) for name, err in report.failed.items()},
    }

    try:
        diagnostics["registers"] = await coordinator.device.async_read_raw()
    except ModbusError as err:
        # Better to hand over the report than to fail the download outright.
        diagnostics["registers_error"] = str(err)

    return diagnostics
