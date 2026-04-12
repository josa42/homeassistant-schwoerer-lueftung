from __future__ import annotations

from typing import Any

from homeassistant.components.climate import (
    ClimateEntity,
)
from homeassistant.components.climate.const import (
    ClimateEntityFeature,
    HVACMode,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import ATTR_TEMPERATURE, UnitOfTemperature
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from custom_components.schwoerer_lueftung.modbus.registers import (
    REG_AUXILIARY_HEATING_ENABLED_ROOM_1,
    REG_CURRENT_TEMPERATURE_ROOM_1,
    REG_TARGET_TEMPERATURE_ROOM_1,
    room_reg,
)
from custom_components.schwoerer_lueftung.modbus.transforms import to_temperature

from .abstract import Entity
from .const import CONF_ROOMS, DOMAIN
from .coordinator import Coordinator


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    coordinator: Coordinator = hass.data[DOMAIN][entry.entry_id]

    # Only create climate entities for WGT devices (with heating)
    if coordinator.has_heating():
        rooms: list[dict[str, Any]] = entry.data.get(CONF_ROOMS, [])

        entities = [RoomClimate(coordinator, room["number"]) for room in rooms]

        async_add_entities(entities)


class RoomClimate(Entity, ClimateEntity):
    """
    Climate entity for controlling room temperature and HVAC mode.
    (Raumklima)

    Registers:
        - 360-376: Current Temperature Room 1-17 (read-only, value / 10 = °C)
        - 400-416: Target Temperature Room 1-17 (value / 10 = °C)
        - 440-456: Auxiliary Heating Enabled Room 1-17 (0=Off, 1=On)
    """

    def __init__(self, coordinator: Coordinator, room_number: int) -> None:
        super().__init__(
            coordinator,
            entity_type="climate_room",
            device=coordinator.get_room_device(room_number),
        )

        self._room_number = room_number
        self._attr_unique_id = (
            f"{coordinator.config_entry.entry_id}_room_{room_number}_climate"
        )
        self._attr_temperature_unit = UnitOfTemperature.CELSIUS
        self._attr_supported_features = ClimateEntityFeature.TARGET_TEMPERATURE
        self._attr_hvac_modes = [HVACMode.FAN_ONLY, HVACMode.HEAT]
        self._attr_min_temp = 10.0
        self._attr_max_temp = 30.0
        self._attr_target_temperature_room_step = 0.5

    @property
    def current_temperature(self) -> float | None:
        raw_value = self.coordinator.get_room_data(
            REG_CURRENT_TEMPERATURE_ROOM_1, self._room_number
        )
        return to_temperature(raw_value)

    @property
    def target_temperature(self) -> float | None:
        raw_value = self.coordinator.get_room_data(
            REG_TARGET_TEMPERATURE_ROOM_1, self._room_number
        )
        return to_temperature(raw_value)

    @property
    def hvac_mode(self) -> HVACMode:
        return self.coordinator.get_room_data(
            REG_AUXILIARY_HEATING_ENABLED_ROOM_1,
            self._room_number,
            {
                1: HVACMode.HEAT,
                0: HVACMode.FAN_ONLY,
            },
        )

    @property
    def extra_state_attributes(self) -> dict:
        """Return the entity type as an attribute."""
        return {
            "entity_type": self._entity_type,
            "room_number": self._room_number,
        }

    async def async_set_temperature(self, **kwargs: Any) -> None:
        if (temperature := kwargs.get(ATTR_TEMPERATURE)) is not None:
            # Clamp temperature to valid range
            temperature = max(
                self._attr_min_temp, min(self._attr_max_temp, temperature)
            )

            await self.coordinator.async_write_register(
                room_reg(REG_TARGET_TEMPERATURE_ROOM_1, self._room_number),
                int(temperature * 10),
            )

    async def async_set_hvac_mode(self, hvac_mode: HVACMode) -> None:
        await self.coordinator.async_write_room_register(
            REG_AUXILIARY_HEATING_ENABLED_ROOM_1,
            self._room_number,
            1 if hvac_mode == HVACMode.HEAT else 0,
        )
