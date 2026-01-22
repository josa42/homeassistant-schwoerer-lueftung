from __future__ import annotations

import logging
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
    REG_CURRENT_TEMPERATURE_1,
    REG_AUXILIARY_HEATING_ENABLED_ROOM_1,
    REG_TARGET_TEMPERATURE_1,
    room_reg,
)

from .const import CONF_ROOMS, DOMAIN
from .coordinator import Coordinator
from .entity import Entity

async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    coordinator: Coordinator = hass.data[DOMAIN][entry.entry_id]

    # Only create climate entities for WGT devices (with heating)
    if not coordinator.has_heating():
        return

    rooms: list[dict[str, Any]] = entry.data.get(CONF_ROOMS, [])

    entities = [
        RoomClimate(coordinator, room["number"], room["name"])
        for room in rooms
    ]

    async_add_entities(entities)


class RoomClimate(Entity, ClimateEntity):
    """Climate entity for a room."""

    _attr_temperature_unit = UnitOfTemperature.CELSIUS
    _attr_supported_features = ClimateEntityFeature.TARGET_TEMPERATURE
    _attr_hvac_modes = [HVACMode.FAN_ONLY, HVACMode.HEAT]
    _attr_min_temp = 10.0
    _attr_max_temp = 30.0
    _attr_target_temperature_step = 0.5

    def __init__(
        self, coordinator: Coordinator, room_number: int, room_name: str
    ) -> None:
        """Initialize the climate entity."""
        super().__init__(coordinator)

        # Validate room number (1-17 as per Modbus documentation)
        if not 1 <= room_number <= 17:
            raise ValueError(f"Room number must be between 1 and 17, got {room_number}")

        self._room_number = room_number
        self._room_name = room_name
        self._attr_unique_id = f"{coordinator.config_entry.entry_id}_{room_name.lower().replace(' ', '_')}_climate"
        self._attr_translation_key = "room_climate"
        self._attr_translation_placeholders = {"room_name": room_name}

        # Room-specific device
        self._attr_device_info = coordinator.get_room_device(room_number)

    @property
    def current_temperature(self) -> float | None:
        """Return the current temperature."""
        return self.coordinator.get_room_data(REG_CURRENT_TEMPERATURE_1, self._room_number)

    @property
    def target_temperature(self) -> float | None:
        """Return the target temperature."""
        return self.coordinator.get_room_data(REG_TARGET_TEMPERATURE_1, self._room_number)

    @property
    def hvac_mode(self) -> HVACMode:
        """Return current HVAC mode."""

        return self.coordinator.get_room_data(REG_AUXILIARY_HEATING_ENABLED_ROOM_1, self._room_number, {
            1: HVACMode.HEAT,
            0: HVACMode.FAN_ONLY,
        })


    async def async_set_temperature(self, **kwargs: Any) -> None:
        """Set new target temperature."""
        if (temperature := kwargs.get(ATTR_TEMPERATURE)) is None:
            return

        # Clamp temperature to valid range
        temperature = max(self._attr_min_temp, min(self._attr_max_temp, temperature))

        await self.coordinator.async_write_register(
            room_reg(REG_TARGET_TEMPERATURE_1, self._room_number), int(temperature * 10)
        )

    async def async_set_hvac_mode(self, hvac_mode: HVACMode) -> None:
        """Set HVAC mode."""

        # Map HVAC mode to register value
        if hvac_mode == HVACMode.HEAT:
            value = 1  # Heizen frei
        else:  # HVACMode.FAN_ONLY
            value = 0  # Gesperrt

        await self.coordinator.async_write_room_register(
            REG_AUXILIARY_HEATING_ENABLED_ROOM_1, self._room_number, value
        )
