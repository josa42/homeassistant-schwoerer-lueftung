"""Climate platform for Schwörer Lüftung."""

from __future__ import annotations

from typing import Any

from homeassistant.components.climate import ClimateEntity
from homeassistant.components.climate.const import ClimateEntityFeature, HVACMode
from homeassistant.const import ATTR_TEMPERATURE, UnitOfTemperature
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import CONF_ROOMS
from .coordinator import Coordinator, SchwoererConfigEntry
from .device.components import ROOM_TEMPERATURE_MAX, ROOM_TEMPERATURE_MIN
from .entity import ROOMS, SchwoererEntity, SchwoererEntityDescription

# The room's current temperature is what this entity is "keyed" on; the target
# and the heating enable are read off the same room component.
ROOM_CLIMATE = SchwoererEntityDescription(
    key="climate_room",
    subsystem=ROOMS,
    field="current_temperature",
)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: SchwoererConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    coordinator = entry.runtime_data

    # Only a WGT can heat a room.
    if not coordinator.has_heating():
        return

    async_add_entities(
        RoomClimate(coordinator, room["number"])
        for room in entry.data.get(CONF_ROOMS, [])
    )


class RoomClimate(SchwoererEntity, ClimateEntity):
    """Room temperature and heating mode. (Raumklima)"""

    _attr_temperature_unit = UnitOfTemperature.CELSIUS
    _attr_supported_features = ClimateEntityFeature.TARGET_TEMPERATURE
    _attr_hvac_modes = [HVACMode.FAN_ONLY, HVACMode.HEAT]
    _attr_min_temp = ROOM_TEMPERATURE_MIN
    _attr_max_temp = ROOM_TEMPERATURE_MAX
    _attr_target_temperature_step = 0.5

    def __init__(self, coordinator: Coordinator, room_number: int) -> None:
        super().__init__(coordinator, ROOM_CLIMATE, room_number)

        # Predates the shared unique_id scheme, so it is spelled out to keep
        # the entity's history across the upgrade.
        self._attr_unique_id = (
            f"{coordinator.config_entry.entry_id}_room_{room_number}_climate"
        )
        self._attr_translation_key = ROOM_CLIMATE.key

    @property
    def current_temperature(self) -> float | None:
        return self._value

    @property
    def target_temperature(self) -> float | None:
        component = self._component
        return None if component is None else component.target_temperature

    @property
    def hvac_mode(self) -> HVACMode | None:
        component = self._component
        if component is None or component.auxiliary_heating_enabled is None:
            return None
        return (
            HVACMode.HEAT
            if component.auxiliary_heating_enabled == 1
            else HVACMode.FAN_ONLY
        )

    async def async_set_temperature(self, **kwargs: Any) -> None:
        if (temperature := kwargs.get(ATTR_TEMPERATURE)) is None:
            return

        component = self._component
        if component is None:
            return

        # Clamp rather than let the field's validator reject: a thermostat card
        # can ask for a value outside the device's range.
        temperature = max(self._attr_min_temp, min(self._attr_max_temp, temperature))
        await self.coordinator.async_write(component, "target_temperature", temperature)

    async def async_set_hvac_mode(self, hvac_mode: HVACMode) -> None:
        component = self._component
        if component is None:
            return

        await self.coordinator.async_write(
            component,
            "auxiliary_heating_enabled",
            1 if hvac_mode == HVACMode.HEAT else 0,
        )
