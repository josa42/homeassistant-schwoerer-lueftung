"""Binary sensor platform for Schwörer Lüftung."""

from __future__ import annotations

from dataclasses import dataclass

from homeassistant.components.binary_sensor import (
    BinarySensorDeviceClass,
    BinarySensorEntity,
    BinarySensorEntityDescription,
)
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import CONF_ROOMS
from .coordinator import SchwoererConfigEntry
from .entity import ROOMS, SchwoererEntity, SchwoererEntityDescription

# Vorheizregister Zustand: 0=off, 1=VHR 1, 2=VHR 2, 3=VHR 1 & 2.
PREHEATER_COIL_1_ACTIVE = {1, 3}
PREHEATER_COIL_2_ACTIVE = {2, 3}


@dataclass(frozen=True, kw_only=True)
class SchwoererBinarySensorEntityDescription(
    SchwoererEntityDescription, BinarySensorEntityDescription
):
    """Describe a binary sensor backed by a device field."""


def _alarm(key: str, *, enabled: bool) -> SchwoererBinarySensorEntityDescription:
    return SchwoererBinarySensorEntityDescription(
        key=key,
        subsystem="alarms",
        device_class=BinarySensorDeviceClass.PROBLEM,
        entity_registry_enabled_default=enabled,
    )


COMMON_BINARY_SENSORS: tuple[SchwoererBinarySensorEntityDescription, ...] = (
    SchwoererBinarySensorEntityDescription(key="fan_override", subsystem="ventilation"),
    SchwoererBinarySensorEntityDescription(
        key="outdoor_damper_state",
        subsystem="ventilation",
        entity_registry_enabled_default=False,
    ),
    _alarm("alarm_pressure_switch", enabled=False),
    _alarm("alarm_utility_lock", enabled=False),
    _alarm("alarm_door_open", enabled=True),
    _alarm("alarm_device_filter_dirty", enabled=True),
    _alarm("alarm_upstream_filter_dirty", enabled=True),
    _alarm("alarm_off_peak_disabled", enabled=False),
    _alarm("alarm_supply_voltage_off", enabled=False),
    _alarm("alarm_pressostat_triggered", enabled=False),
    _alarm("alarm_external_utility_lock", enabled=False),
    _alarm("alarm_emergency_mode", enabled=True),
)

HEATING_BINARY_SENSORS: tuple[SchwoererBinarySensorEntityDescription, ...] = (
    SchwoererBinarySensorEntityDescription(
        key="reheater_state",
        subsystem="heating",
        entity_registry_enabled_default=False,
    ),
    # Both coils are reported by one register, so each entity tests the
    # values that mean its own coil is running.
    SchwoererBinarySensorEntityDescription(
        key="preheater_1",
        subsystem="ventilation",
        field="preheater_state",
        value_fn=lambda value: value in PREHEATER_COIL_1_ACTIVE,
        entity_registry_enabled_default=False,
    ),
    SchwoererBinarySensorEntityDescription(
        key="preheater_2",
        subsystem="ventilation",
        field="preheater_state",
        value_fn=lambda value: value in PREHEATER_COIL_2_ACTIVE,
        entity_registry_enabled_default=False,
    ),
    _alarm("alarm_heating_module_test", enabled=False),
    _alarm("alarm_supply_air_cold", enabled=True),
)

ROOM_BINARY_SENSORS: tuple[SchwoererBinarySensorEntityDescription, ...] = (
    SchwoererBinarySensorEntityDescription(
        key="auxiliary_heating_enabled",
        subsystem=ROOMS,
        entity_registry_enabled_default=False,
    ),
    SchwoererBinarySensorEntityDescription(
        key="auxiliary_heating_active",
        subsystem=ROOMS,
        device_class=BinarySensorDeviceClass.HEAT,
    ),
)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: SchwoererConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    coordinator = entry.runtime_data

    entities = [
        SchwoererBinarySensor(coordinator, description)
        for description in COMMON_BINARY_SENSORS
    ]

    if coordinator.has_heating():
        entities.extend(
            SchwoererBinarySensor(coordinator, description)
            for description in HEATING_BINARY_SENSORS
        )
        entities.extend(
            SchwoererBinarySensor(coordinator, description, room["number"])
            for room in entry.data.get(CONF_ROOMS, [])
            for description in ROOM_BINARY_SENSORS
        )

    async_add_entities(entities)


class SchwoererBinarySensor(SchwoererEntity, BinarySensorEntity):
    """A binary sensor reading one device field."""

    entity_description: SchwoererBinarySensorEntityDescription

    @property
    def is_on(self) -> bool | None:
        value = self._value
        if value is None:
            return None
        # value_fn already reduced the multi-state registers to a bool.
        return value if isinstance(value, bool) else value == 1
