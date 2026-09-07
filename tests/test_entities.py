"""Entity-level tests.

The unique_id cases are the important ones. Entities carry their history on
their unique_id, so an id that shifts in the 2.0 rewrite silently orphans a
user's statistics, customisations and automations. The expected values below
were taken from the pre-2.0 code, where they were built as
``f"{entry_id}_{REG_KEYS[address]}"``.
"""

from __future__ import annotations

from datetime import datetime

import pytest
from homeassistant.const import EntityCategory
from homeassistant.core import HomeAssistant
from homeassistant.helpers import entity_registry as er
from homeassistant.util import dt as dt_util
from modbus_connection import IllegalDataAddressError
from modbus_connection.mock import MockModbusUnit
from pytest_homeassistant_custom_component.common import MockConfigEntry

# key -> the unique_id suffix the 1.x code produced. Room entities appended the
# room number to the register's key; the climate entity had its own scheme.
EXPECTED_UNIQUE_ID_SUFFIXES = {
    "sensor.current_fan_level": "current_fan_level",
    "sensor.temperature_t10_outdoor": "temperature_t10_outdoor",
    "sensor.error_message": "error_message",
    "sensor.heat_pump_status": "heat_pump_status",
    "binary_sensor.fan_override": "fan_override",
    "binary_sensor.alarm_door_open": "alarm_door_open",
    "select.operation_mode": "operation_mode",
    "select.fan_speed": "fan_speed",
    "switch.shock_ventilation": "shock_ventilation",
}


async def setup_entry(hass: HomeAssistant, entry: MockConfigEntry) -> None:
    entry.add_to_hass(hass)
    assert await hass.config_entries.async_setup(entry.entry_id)
    await hass.async_block_till_done()


def unique_ids(hass: HomeAssistant, entry: MockConfigEntry) -> set[str]:
    registry = er.async_get(hass)
    return {
        er_entry.unique_id
        for er_entry in er.async_entries_for_config_entry(registry, entry.entry_id)
    }


async def test_global_unique_ids_are_unchanged(
    hass: HomeAssistant, mock_modbus, wgt_entry: MockConfigEntry
) -> None:
    await setup_entry(hass, wgt_entry)

    ids = unique_ids(hass, wgt_entry)
    for suffix in EXPECTED_UNIQUE_ID_SUFFIXES.values():
        assert f"{wgt_entry.entry_id}_{suffix}" in ids


@pytest.mark.parametrize(
    "suffix",
    [
        "base_temperature_room_1",
        "auxiliary_heating_enabled_room_2",
        "auxiliary_heating_active_room_1",
        "scheduled_heating_enabled_room_2",
    ],
)
async def test_room_unique_ids_are_unchanged(
    hass: HomeAssistant, mock_modbus, wgt_entry: MockConfigEntry, suffix: str
) -> None:
    """1.x built these from REG_KEYS[base + (n - 1)], e.g. base_temperature_room_2."""
    await setup_entry(hass, wgt_entry)

    assert f"{wgt_entry.entry_id}_{suffix}" in unique_ids(hass, wgt_entry)


@pytest.mark.parametrize(
    "suffix", ["current_temperature_room_1", "current_temperature_room_2"]
)
async def test_wrt_room_temperature_unique_ids_are_unchanged(
    hass: HomeAssistant, mock_modbus, wrt_entry: MockConfigEntry, suffix: str
) -> None:
    """Only a WRT gets a room temperature sensor; a WGT gets a climate entity."""
    await setup_entry(hass, wrt_entry)

    assert f"{wrt_entry.entry_id}_{suffix}" in unique_ids(hass, wrt_entry)


async def test_room_climate_keeps_its_own_unique_id(
    hass: HomeAssistant, mock_modbus, wgt_entry: MockConfigEntry
) -> None:
    """The climate entity predates the shared scheme and must keep its own."""
    await setup_entry(hass, wgt_entry)

    ids = unique_ids(hass, wgt_entry)
    assert f"{wgt_entry.entry_id}_room_1_climate" in ids
    assert f"{wgt_entry.entry_id}_room_2_climate" in ids


async def test_translation_keys_are_unchanged(
    hass: HomeAssistant, mock_modbus, wgt_entry: MockConfigEntry
) -> None:
    """Room entities key off the field name with `_room` appended, as before."""
    await setup_entry(hass, wgt_entry)

    registry = er.async_get(hass)
    entries = {
        e.unique_id: e
        for e in er.async_entries_for_config_entry(registry, wgt_entry.entry_id)
    }

    room = entries[f"{wgt_entry.entry_id}_base_temperature_room_1"]
    assert room.translation_key == "base_temperature_room"

    fan = entries[f"{wgt_entry.entry_id}_current_fan_level"]
    assert fan.translation_key == "current_fan_level"

    climate = entries[f"{wgt_entry.entry_id}_room_1_climate"]
    assert climate.translation_key == "climate_room"


async def test_values_and_attributes(
    hass: HomeAssistant, mock_modbus, wgt_entry: MockConfigEntry
) -> None:
    await setup_entry(hass, wgt_entry)

    outdoor = hass.states.get("sensor.wgt_t10_aussen") or _by_unique_id(
        hass, wgt_entry, "temperature_t10_outdoor"
    )
    assert outdoor is not None
    assert float(outdoor.state) == 7.8
    assert outdoor.attributes["entity_type"] == "temperature_t10_outdoor"

    heat_pump = _by_unique_id(hass, wgt_entry, "heat_pump_status")
    assert heat_pump is not None
    assert heat_pump.state == "heating"


async def test_room_attributes_carry_the_room_number(
    hass: HomeAssistant, mock_modbus, wgt_entry: MockConfigEntry
) -> None:
    await setup_entry(hass, wgt_entry)

    state = _by_unique_id(hass, wgt_entry, "auxiliary_heating_active_room_2")
    assert state is not None
    assert state.attributes["room_number"] == 2
    assert state.attributes["entity_type"] == "auxiliary_heating_active_room"


async def test_entities_go_unavailable_only_with_their_own_subsystem(
    hass: HomeAssistant,
    mock_modbus,
    unit: MockModbusUnit,
    wgt_entry: MockConfigEntry,
) -> None:
    """A refused heat pump takes down the heating entities and nothing else."""
    await setup_entry(hass, wgt_entry)

    for address in (114, 115, 116):
        unit.fail_read(address, IllegalDataAddressError(2))

    await wgt_entry.runtime_data.async_refresh()
    await hass.async_block_till_done()

    assert _by_unique_id(hass, wgt_entry, "heat_pump_status").state == "unavailable"
    assert _by_unique_id(hass, wgt_entry, "current_fan_level").state != "unavailable"
    assert (
        _by_unique_id(hass, wgt_entry, "temperature_t10_outdoor").state != "unavailable"
    )


async def _enable(hass: HomeAssistant, entry: MockConfigEntry, *suffixes: str) -> None:
    """Turn entities on the way the entity page does, then reload."""
    registry = er.async_get(hass)
    wanted = {f"{entry.entry_id}_{s}" for s in suffixes}
    for er_entry in er.async_entries_for_config_entry(registry, entry.entry_id):
        if er_entry.unique_id in wanted:
            registry.async_update_entity(er_entry.entity_id, disabled_by=None)
    await hass.config_entries.async_reload(entry.entry_id)
    await hass.async_block_till_done()


def _by_unique_id(hass: HomeAssistant, entry: MockConfigEntry, suffix: str):
    """Look a state up by the unique_id suffix, not by a guessed entity_id."""
    registry = er.async_get(hass)
    for er_entry in er.async_entries_for_config_entry(registry, entry.entry_id):
        if er_entry.unique_id == f"{entry.entry_id}_{suffix}":
            return hass.states.get(er_entry.entity_id)
    return None


async def test_undocumented_sensors_render(
    hass: HomeAssistant, mock_modbus, wgt_entry: MockConfigEntry
) -> None:
    """T9 and the device clock, which ship disabled, produce sane states.

    Enabled the way a user would: switch them on in the entity page, which
    reloads the entry.
    """
    await setup_entry(hass, wgt_entry)
    await _enable(hass, wgt_entry, "temperature_t9", "device_clock")

    t9 = _by_unique_id(hass, wgt_entry, "temperature_t9")
    assert t9 is not None
    assert float(t9.state) == 25.9
    assert t9.attributes["entity_type"] == "temperature_t9"

    clock = _by_unique_id(hass, wgt_entry, "device_clock")
    assert clock is not None
    # A timestamp sensor renders as an ISO string, serialized to UTC. The unit
    # keeps local time with no zone, so it is read as Home Assistant's - the
    # comparison is between instants, not wall clocks.
    parsed = datetime.fromisoformat(clock.state)
    assert parsed.tzinfo is not None
    assert parsed == datetime(2026, 9, 7, 12, 21, 32, tzinfo=dt_util.DEFAULT_TIME_ZONE)


async def test_clock_is_diagnostic_and_off_by_default(
    hass: HomeAssistant, mock_modbus, wgt_entry: MockConfigEntry
) -> None:
    """Undocumented extras must not clutter a fresh install."""
    await setup_entry(hass, wgt_entry)

    registry = er.async_get(hass)
    entries = {
        e.unique_id: e
        for e in er.async_entries_for_config_entry(registry, wgt_entry.entry_id)
    }
    clock = entries[f"{wgt_entry.entry_id}_device_clock"]
    assert clock.disabled_by is er.RegistryEntryDisabler.INTEGRATION
    assert clock.entity_category is EntityCategory.DIAGNOSTIC
    assert entries[f"{wgt_entry.entry_id}_temperature_t9"].disabled_by is not None
