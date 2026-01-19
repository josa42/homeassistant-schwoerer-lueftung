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
    
    entities = [BicWrgShockVentilationSwitch(coordinator, entry)]
    
    # Add room auxiliary heating switches
    rooms = entry.data.get("rooms", [])
    for room in rooms:
        entities.append(
            BicWrgRoomAuxiliaryHeatingActiveSwitch(coordinator, room["number"], room["name"])
        )
    
    async_add_entities(entities)


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


class BicWrgRoomAuxiliaryHeatingActiveSwitch(CoordinatorEntity[BicWrgCoordinator], SwitchEntity):
    """Switch entity for room auxiliary heating active state (Zusatzheizung aktiv)."""

    _attr_has_entity_name = True
    _attr_entity_registry_enabled_default = False

    def __init__(
        self,
        coordinator: BicWrgCoordinator,
        room_number: int,
        room_name: str,
    ) -> None:
        """Initialize the switch entity."""
        super().__init__(coordinator)
        self._room_number = room_number
        self._room_name = room_name
        self._attr_unique_id = f"{coordinator.config_entry.entry_id}_room_{room_number}_auxiliary_heating_active"
        self._attr_name = "Auxiliary Heating Active"
        
        # Room-specific device
        self._attr_device_info = {
            "identifiers": {(DOMAIN, f"{coordinator.config_entry.entry_id}_room_{room_number}")},
            "name": room_name,
            "manufacturer": "BIC",
            "model": "Room Climate Control",
            "via_device": (DOMAIN, coordinator.config_entry.entry_id),
        }

    @property
    def is_on(self) -> bool | None:
        """Return true if auxiliary heating is active."""
        # Register 460-476 for rooms 1-17
        register = 460 + self._room_number - 1
        value = self.coordinator.data.get(f"register_{register}")
        if value is not None:
            return value == 1
        return None

    async def async_turn_on(self, **kwargs: Any) -> None:
        """Turn on auxiliary heating."""
        register = 460 + self._room_number - 1
        success = await self.hass.async_add_executor_job(
            self.coordinator.client.write_register, register, 1
        )
        
        if success:
            await self.coordinator.async_request_refresh()

    async def async_turn_off(self, **kwargs: Any) -> None:
        """Turn off auxiliary heating."""
        register = 460 + self._room_number - 1
        success = await self.hass.async_add_executor_job(
            self.coordinator.client.write_register, register, 0
        )
        
        if success:
            await self.coordinator.async_request_refresh()
