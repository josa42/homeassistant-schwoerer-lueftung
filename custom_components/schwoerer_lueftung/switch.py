"""Switch platform for Schwörer Lüftung."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from homeassistant.components.switch import SwitchEntity, SwitchEntityDescription
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import CONF_ROOMS
from .coordinator import SchwoererConfigEntry
from .entity import ROOMS, SchwoererEntity, SchwoererEntityDescription


@dataclass(frozen=True, kw_only=True)
class SchwoererSwitchEntityDescription(
    SchwoererEntityDescription, SwitchEntityDescription
):
    """Describe a switch backed by a writable device field."""


COMMON_SWITCHES: tuple[SchwoererSwitchEntityDescription, ...] = (
    SchwoererSwitchEntityDescription(key="shock_ventilation", subsystem="ventilation"),
)

HEATING_SWITCHES: tuple[SchwoererSwitchEntityDescription, ...] = (
    SchwoererSwitchEntityDescription(
        key="heat_pump_heating_enabled", subsystem="heating"
    ),
    SchwoererSwitchEntityDescription(
        key="heat_pump_cooling_enabled", subsystem="heating"
    ),
    SchwoererSwitchEntityDescription(
        key="auxiliary_heating_enabled", subsystem="heating"
    ),
)

ROOM_SWITCHES: tuple[SchwoererSwitchEntityDescription, ...] = (
    SchwoererSwitchEntityDescription(
        key="auxiliary_heating_enabled",
        subsystem=ROOMS,
    ),
    SchwoererSwitchEntityDescription(
        key="scheduled_heating_enabled",
        subsystem=ROOMS,
    ),
)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: SchwoererConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    coordinator = entry.runtime_data

    entities = [
        SchwoererSwitch(coordinator, description) for description in COMMON_SWITCHES
    ]

    if coordinator.has_heating():
        entities.extend(
            SchwoererSwitch(coordinator, description)
            for description in HEATING_SWITCHES
        )
        entities.extend(
            SchwoererSwitch(coordinator, description, room["number"])
            for room in entry.data.get(CONF_ROOMS, [])
            for description in ROOM_SWITCHES
        )

    async_add_entities(entities)


class SchwoererSwitch(SchwoererEntity, SwitchEntity):
    """A switch over a writable 0/1 device field."""

    entity_description: SchwoererSwitchEntityDescription

    @property
    def is_on(self) -> bool | None:
        value = self._value
        return value == 1 if value is not None else None

    async def async_turn_on(self, **kwargs: Any) -> None:
        await self._async_write(1)

    async def async_turn_off(self, **kwargs: Any) -> None:
        await self._async_write(0)
