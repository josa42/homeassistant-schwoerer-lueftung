"""Climate platform for BIC WRG."""
from __future__ import annotations

from typing import Any

from homeassistant.components.climate import (
    ClimateEntity,
    ClimateEntityFeature,
    HVACMode,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import UnitOfTemperature
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity import DeviceInfo
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN, MANUFACTURER, MODEL
from .coordinator import BicWrgCoordinator


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up WRG climate from a config entry."""
    coordinator: BicWrgCoordinator = hass.data[DOMAIN][entry.entry_id]
    
    async_add_entities([BicWrgClimate(coordinator, entry)])


class BicWrgClimate(CoordinatorEntity[BicWrgCoordinator], ClimateEntity):
    """Climate entity for WRG ventilation system."""

    _attr_temperature_unit = UnitOfTemperature.CELSIUS
    _attr_supported_features = ClimateEntityFeature.TARGET_TEMPERATURE
    _attr_hvac_modes = [HVACMode.OFF, HVACMode.AUTO, HVACMode.HEAT]

    def __init__(
        self,
        coordinator: BicWrgCoordinator,
        entry: ConfigEntry,
    ) -> None:
        """Initialize the climate entity."""
        super().__init__(coordinator)
        self._attr_name = "WRG Climate"
        self._attr_unique_id = f"{entry.entry_id}_climate"
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, entry.entry_id)},
            name="WRG 134-BP-HK",
            manufacturer=MANUFACTURER,
            model=MODEL,
        )

    @property
    def hvac_mode(self) -> HVACMode:
        """Return current HVAC mode."""
        # TODO: Map device state to HVAC mode
        return HVACMode.AUTO

    @property
    def current_temperature(self) -> float | None:
        """Return the current temperature."""
        # TODO: Get actual temperature from coordinator data
        return self.coordinator.data.get("supply_temp")

    @property
    def target_temperature(self) -> float | None:
        """Return the target temperature."""
        # TODO: Get actual target temperature from coordinator data
        return self.coordinator.data.get("target_temp")

    async def async_set_hvac_mode(self, hvac_mode: HVACMode) -> None:
        """Set new HVAC mode."""
        # TODO: Implement mode setting via Modbus
        pass

    async def async_set_temperature(self, **kwargs: Any) -> None:
        """Set new target temperature."""
        # TODO: Implement temperature setting via Modbus
        pass
