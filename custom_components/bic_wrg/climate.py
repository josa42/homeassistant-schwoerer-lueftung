"""Climate platform for BIC WRG integration."""
from __future__ import annotations

import logging
from typing import Any

from homeassistant.components.climate import (
    ClimateEntity,
    ClimateEntityFeature,
    HVACMode,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import ATTR_TEMPERATURE, UnitOfTemperature
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import CONF_ROOMS, DOMAIN
from .coordinator import BicWrgCoordinator
from .entity import BicWrgEntity

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up BIC WRG climate entities."""
    coordinator: BicWrgCoordinator = hass.data[DOMAIN][entry.entry_id]
    rooms: list[dict[str, Any]] = entry.data.get(CONF_ROOMS, [])

    entities = [
        BicWrgRoomClimate(coordinator, room["number"], room["name"])
        for room in rooms
    ]

    async_add_entities(entities)


class BicWrgRoomClimate(BicWrgEntity, ClimateEntity):
    """Climate entity for a room."""

    _attr_temperature_unit = UnitOfTemperature.CELSIUS
    _attr_supported_features = ClimateEntityFeature.TARGET_TEMPERATURE
    _attr_hvac_modes = [HVACMode.FAN_ONLY, HVACMode.HEAT]
    _attr_min_temp = 10.0
    _attr_max_temp = 30.0
    _attr_target_temperature_step = 0.5

    def __init__(
        self, coordinator: BicWrgCoordinator, room_number: int, room_name: str
    ) -> None:
        """Initialize the climate entity."""
        super().__init__(coordinator)
        self._room_number = room_number
        self._room_name = room_name
        self._attr_unique_id = f"{coordinator.config_entry.entry_id}_{room_name.lower().replace(' ', '_')}_climate"
        self._attr_translation_key = "room_climate"
        self._attr_translation_placeholders = {"room_name": room_name}
        
        # Room-specific device
        self._attr_device_info = {
            "identifiers": {(DOMAIN, f"{coordinator.config_entry.entry_id}_room_{room_number}")},
            "name": room_name,
            "manufacturer": MANUFACTURER,
            "model": "Room Climate Control",
            "via_device": (DOMAIN, coordinator.config_entry.entry_id),
        }

    @property
    def current_temperature(self) -> float | None:
        """Return the current temperature."""
        # Register 360-376 for rooms 1-17
        register = 360 + self._room_number - 1
        value = self.coordinator.data.get(f"register_{register}")
        if value is None:
            return None
        return value / 10.0

    @property
    def target_temperature(self) -> float | None:
        """Return the target temperature."""
        # Register 400-416 for rooms 1-17
        register = 400 + self._room_number - 1
        value = self.coordinator.data.get(f"register_{register}")
        if value is None:
            return None
        return value / 10.0

    @property
    def hvac_mode(self) -> HVACMode:
        """Return current HVAC mode."""
        # Register 440-451 for rooms 1-12 (only rooms 1-12 have heating control)
        if self._room_number > 12:
            return HVACMode.FAN_ONLY
            
        register = 440 + self._room_number - 1
        value = self.coordinator.data.get(f"register_{register}")
        
        if value == 1:
            return HVACMode.HEAT
        else:
            return HVACMode.FAN_ONLY

    async def async_set_temperature(self, **kwargs: Any) -> None:
        """Set new target temperature."""
        if (temperature := kwargs.get(ATTR_TEMPERATURE)) is None:
            return

        # Clamp temperature to valid range
        temperature = max(self._attr_min_temp, min(self._attr_max_temp, temperature))
        
        # Convert to register value (multiply by 10)
        value = int(temperature * 10)
        
        # Register 400-416 for rooms 1-17
        register = 400 + self._room_number - 1
        
        await self.coordinator.write_register(register, value)
        await self.coordinator.async_request_refresh()

    async def async_set_hvac_mode(self, hvac_mode: HVACMode) -> None:
        """Set HVAC mode."""
        # Register 440-451 for rooms 1-12 (only rooms 1-12 have heating control)
        if self._room_number > 12:
            return
        
        # Map HVAC mode to register value
        if hvac_mode == HVACMode.HEAT:
            value = 1  # Heizen frei
        else:  # HVACMode.FAN_ONLY
            value = 0  # Gesperrt
        
        await self.coordinator.write_room_heating_enable(self._room_number, value)
        await self.coordinator.async_request_refresh()
