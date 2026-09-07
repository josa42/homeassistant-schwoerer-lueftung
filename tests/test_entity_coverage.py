"""Guard against an entity being dropped in a refactor.

Every translated entity key must be produced by some entity description, and
every description must have a translation. The 2.0 rewrite replaced ~60 entity
classes with descriptions, and this is what catches one going missing in the
process - it caught `operating_hours_ground_heat_exchanger`, which the first
pass lost.
"""

from __future__ import annotations

from custom_components.schwoerer_lueftung import (
    binary_sensor as binary_sensor_platform,
)
from custom_components.schwoerer_lueftung import climate as climate_platform
from custom_components.schwoerer_lueftung import number as number_platform
from custom_components.schwoerer_lueftung import select as select_platform
from custom_components.schwoerer_lueftung import sensor as sensor_platform
from custom_components.schwoerer_lueftung import switch as switch_platform
from custom_components.schwoerer_lueftung.entity import ROOMS

from .test_translations import VALID_ENTITY_KEYS


def _keys(descriptions) -> set[str]:
    """Translation keys the descriptions produce, room suffix included."""
    return {f"{d.key}_room" if d.subsystem == ROOMS else d.key for d in descriptions}


IMPLEMENTED: dict[str, set[str]] = {
    "sensor": _keys(
        [
            *sensor_platform.VENTILATION_SENSORS,
            *sensor_platform.TEMPERATURE_SENSORS,
            *sensor_platform.ALARM_SENSORS,
            *sensor_platform.OPERATING_HOURS_SENSORS,
            *sensor_platform.HEATING_SENSORS,
            *sensor_platform.GROUND_HEAT_EXCHANGER_SENSORS,
            sensor_platform.CLOCK_SENSOR,
            sensor_platform.ROOM_SENSOR,
        ]
    ),
    "binary_sensor": _keys(
        [
            *binary_sensor_platform.COMMON_BINARY_SENSORS,
            *binary_sensor_platform.HEATING_BINARY_SENSORS,
            *binary_sensor_platform.ROOM_BINARY_SENSORS,
        ]
    ),
    "switch": _keys(
        [
            *switch_platform.COMMON_SWITCHES,
            *switch_platform.HEATING_SWITCHES,
            *switch_platform.ROOM_SWITCHES,
        ]
    ),
    "select": _keys(
        [*select_platform.COMMON_SELECTS, *select_platform.HEATING_SELECTS]
    ),
    "number": _keys([*number_platform.COMMON_NUMBERS, *number_platform.ROOM_NUMBERS]),
    "climate": {climate_platform.ROOM_CLIMATE.key},
}


def test_every_translated_key_has_an_entity() -> None:
    """A key with a translation but no entity means one was dropped."""
    for platform, translated in VALID_ENTITY_KEYS.items():
        if platform == "device":  # device names, not entities
            continue
        assert not set(translated) - IMPLEMENTED[platform], (
            f"{platform}: translated but no entity creates it: "
            f"{sorted(set(translated) - IMPLEMENTED[platform])}"
        )


def test_every_entity_has_a_translation() -> None:
    for platform, implemented in IMPLEMENTED.items():
        translated = set(VALID_ENTITY_KEYS[platform])
        assert not implemented - translated, (
            f"{platform}: entity exists but is untranslated: "
            f"{sorted(implemented - translated)}"
        )


# Which sensors a fresh install shows. Pinned deliberately: the choice is a
# curation call, not an accident, and `entity_registry_enabled_default` is
# applied only at first registration - so getting it wrong is not something a
# user can be talked through fixing later, entity by entity.
ENABLED_SENSORS = {
    # Air path: outdoor in, supply into the house, extract back out.
    "temperature_t10_outdoor",
    "temperature_t4_after_reheater",
    "temperature_t5_exhaust_air",
    "current_temperature_room",
    # What the unit is doing right now.
    "current_fan_level",
    "current_supply_air_flow",
    "current_exhaust_air_flow",
    "bypass_state",
    "heat_pump_status",
    "shock_ventilation_remaining",
    # Maintenance and faults.
    "error_message",
    "device_filter_remaining",
    "upstream_filter_remaining",
    "operating_hours_fan",
    # Only created when the user declared the hardware at setup.
    "temperature_t1_after_ground_heat_exchanger",
    "ground_heat_exchanger_state",
}


def test_sensor_defaults_are_deliberate() -> None:
    descriptions = [
        *sensor_platform.VENTILATION_SENSORS,
        *sensor_platform.TEMPERATURE_SENSORS,
        *sensor_platform.ALARM_SENSORS,
        *sensor_platform.OPERATING_HOURS_SENSORS,
        *sensor_platform.HEATING_SENSORS,
        *sensor_platform.GROUND_HEAT_EXCHANGER_SENSORS,
        sensor_platform.CLOCK_SENSOR,
        sensor_platform.ROOM_SENSOR,
    ]
    enabled = {
        f"{d.key}_room" if d.subsystem == ROOMS else d.key
        for d in descriptions
        if d.entity_registry_enabled_default
    }
    assert enabled == ENABLED_SENSORS


def test_undocumented_sensors_ship_disabled() -> None:
    """Registers found by probing one unit must not be on for everyone."""
    assert not sensor_platform.CLOCK_SENSOR.entity_registry_enabled_default
    t9 = next(
        d for d in sensor_platform.TEMPERATURE_SENSORS if d.key == "temperature_t9"
    )
    assert not t9.entity_registry_enabled_default
