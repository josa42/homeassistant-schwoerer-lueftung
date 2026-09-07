"""Number platform for Schwörer Lüftung."""

from __future__ import annotations

from dataclasses import dataclass

from homeassistant.components.number import (
    NumberDeviceClass,
    NumberEntity,
    NumberEntityDescription,
    NumberMode,
)
from homeassistant.const import UnitOfTemperature
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import CONF_ROOMS
from .coordinator import SchwoererConfigEntry
from .device.components import (
    LINEAR_FAN_POWER_MAX,
    LINEAR_FAN_POWER_MIN,
    ROOM_TEMPERATURE_MAX,
    ROOM_TEMPERATURE_MIN,
)
from .entity import ROOMS, SchwoererEntity, SchwoererEntityDescription


@dataclass(frozen=True, kw_only=True)
class SchwoererNumberEntityDescription(
    SchwoererEntityDescription, NumberEntityDescription
):
    """Describe a number over a writable device field."""


COMMON_NUMBERS: tuple[SchwoererNumberEntityDescription, ...] = (
    SchwoererNumberEntityDescription(
        key="linear_fan_power",
        subsystem="ventilation",
        native_min_value=LINEAR_FAN_POWER_MIN,
        native_max_value=LINEAR_FAN_POWER_MAX,
        native_step=1,
        native_unit_of_measurement="%",
        entity_registry_enabled_default=False,
    ),
)

ROOM_NUMBERS: tuple[SchwoererNumberEntityDescription, ...] = (
    SchwoererNumberEntityDescription(
        key="base_temperature",
        subsystem=ROOMS,
        device_class=NumberDeviceClass.TEMPERATURE,
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        native_min_value=ROOM_TEMPERATURE_MIN,
        native_max_value=ROOM_TEMPERATURE_MAX,
        native_step=0.1,
        mode=NumberMode.BOX,
        entity_registry_enabled_default=False,
    ),
)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: SchwoererConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    coordinator = entry.runtime_data

    entities = [
        SchwoererNumber(coordinator, description) for description in COMMON_NUMBERS
    ]

    if coordinator.has_heating():
        entities.extend(
            SchwoererNumber(coordinator, description, room["number"])
            for room in entry.data.get(CONF_ROOMS, [])
            for description in ROOM_NUMBERS
        )

    async_add_entities(entities)


class SchwoererNumber(SchwoererEntity, NumberEntity):
    """A number over a writable device field."""

    entity_description: SchwoererNumberEntityDescription

    @property
    def native_value(self) -> float | None:
        return self._value

    async def async_set_native_value(self, value: float) -> None:
        # The field takes the value in its own unit and encodes it; its
        # validator vets the range before anything reaches the wire.
        await self._async_write(value)
