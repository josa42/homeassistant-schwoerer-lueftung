"""Switch platform for BIC WRG."""
from __future__ import annotations

from typing import Any

from homeassistant.components.switch import SwitchEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity import DeviceInfo
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN, MANUFACTURER, MODEL
from .coordinator import BicWrgCoordinator
from .modbus_client import SHOCK_VENTILATION_INACTIVE, SHOCK_VENTILATION_ACTIVE


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up WRG switch entities from a config entry."""
    coordinator: BicWrgCoordinator = hass.data[DOMAIN][entry.entry_id]
    
    async_add_entities([BicWrgShockVentilationSwitch(coordinator, entry)])


class BicWrgShockVentilationSwitch(CoordinatorEntity[BicWrgCoordinator], SwitchEntity):
    """Switch entity for WRG shock ventilation (Stoßlüftung)."""

    _attr_has_entity_name = True
    _attr_name = "Shock Ventilation"

    def __init__(
        self,
        coordinator: BicWrgCoordinator,
        entry: ConfigEntry,
    ) -> None:
        """Initialize the switch entity."""
        super().__init__(coordinator)
        self._attr_unique_id = f"{entry.entry_id}_shock_ventilation"
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, entry.entry_id)},
            name="WRG 134-BP-HK",
            manufacturer=MANUFACTURER,
            model=MODEL,
        )

    @property
    def is_on(self) -> bool | None:
        """Return true if shock ventilation is active."""
        value = self.coordinator.data.get("shock_ventilation")
        if value is not None:
            return value == SHOCK_VENTILATION_ACTIVE
        return None

    async def async_turn_on(self, **kwargs: Any) -> None:
        """Turn on shock ventilation."""
        success = await self.hass.async_add_executor_job(
            self.coordinator.client.write_shock_ventilation, SHOCK_VENTILATION_ACTIVE
        )
        
        if success:
            await self.coordinator.async_request_refresh()

    async def async_turn_off(self, **kwargs: Any) -> None:
        """Turn off shock ventilation."""
        success = await self.hass.async_add_executor_job(
            self.coordinator.client.write_shock_ventilation, SHOCK_VENTILATION_INACTIVE
        )
        
        if success:
            await self.coordinator.async_request_refresh()
