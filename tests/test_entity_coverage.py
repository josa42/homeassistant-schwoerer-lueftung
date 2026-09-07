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


# Entities a fresh install leaves switched off. Everything else is on.
#
# Enabling costs no Modbus traffic - components read every declared field
# whether or not an entity exists - so the only cost is recorder rows. Measured
# against a real unit: temperatures and fan RPM run 17-29 rows a day each,
# everything binary or enum is under one. The whole integration is a few
# hundred rows a day, which is not worth curating around.
#
# So the bar for staying off is narrow: an entity nobody can interpret, one
# that would flood the recorder, or a third view of something already exposed
# twice.
DISABLED_BY_DEFAULT = {
    # Undocumented. Found by probing one unit, and what it measures is unknown,
    # so there is nothing useful to tell a user about it.
    ("sensor", "temperature_t9"),
    # The seconds field ticks, so this writes a recorder row on every poll -
    # about 2880 a day, ten times the rest of the integration, for a
    # diagnostic.
    ("sensor", "device_clock"),
    # Register 440+i already has a switch and drives the room's climate entity.
    ("binary_sensor", "auxiliary_heating_enabled_room"),
}

PLATFORM_DESCRIPTIONS = {
    "sensor": [
        *sensor_platform.VENTILATION_SENSORS,
        *sensor_platform.TEMPERATURE_SENSORS,
        *sensor_platform.ALARM_SENSORS,
        *sensor_platform.OPERATING_HOURS_SENSORS,
        *sensor_platform.HEATING_SENSORS,
        *sensor_platform.GROUND_HEAT_EXCHANGER_SENSORS,
        sensor_platform.CLOCK_SENSOR,
        sensor_platform.ROOM_SENSOR,
    ],
    "binary_sensor": [
        *binary_sensor_platform.COMMON_BINARY_SENSORS,
        *binary_sensor_platform.HEATING_BINARY_SENSORS,
        *binary_sensor_platform.ROOM_BINARY_SENSORS,
    ],
    "switch": [
        *switch_platform.COMMON_SWITCHES,
        *switch_platform.HEATING_SWITCHES,
        *switch_platform.ROOM_SWITCHES,
    ],
    "select": [*select_platform.COMMON_SELECTS, *select_platform.HEATING_SELECTS],
    "number": [*number_platform.COMMON_NUMBERS, *number_platform.ROOM_NUMBERS],
}


def test_only_the_listed_entities_ship_disabled() -> None:
    """Turning an entity off by default should be a deliberate, argued choice."""
    disabled = {
        (platform, f"{d.key}_room" if d.subsystem == ROOMS else d.key)
        for platform, descriptions in PLATFORM_DESCRIPTIONS.items()
        for d in descriptions
        if not d.entity_registry_enabled_default
    }
    assert disabled == DISABLED_BY_DEFAULT


def test_controls_are_never_hidden() -> None:
    """A control a user cannot see is a feature they do not have."""
    for platform in ("switch", "select", "number"):
        for d in PLATFORM_DESCRIPTIONS[platform]:
            assert d.entity_registry_enabled_default, f"{platform}.{d.key} is hidden"
