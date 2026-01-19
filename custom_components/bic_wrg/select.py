"""Select platform for BIC WRG."""
from __future__ import annotations

from homeassistant.components.select import SelectEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity import DeviceInfo
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN, MANUFACTURER, MODEL
from .coordinator import BicWrgCoordinator
from .modbus_client import (
    OPERATION_MODE_OFF,
    OPERATION_MODE_MANUAL,
    OPERATION_MODE_WINTER,
    OPERATION_MODE_SUMMER,
    OPERATION_MODE_SUMMER_EXHAUST,
)

# Operation mode mapping
# Betriebsart: 0=Aus, 1=Handbetrieb, 2=Winterbetrieb, 3=Sommerbetrieb, 4=Sommer Abluft
OPERATION_MODES = {
    OPERATION_MODE_OFF: "Off",
    OPERATION_MODE_MANUAL: "Manual",
    OPERATION_MODE_WINTER: "Winter",
    OPERATION_MODE_SUMMER: "Summer",
    OPERATION_MODE_SUMMER_EXHAUST: "Summer Exhaust",
}


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up WRG select entities from a config entry."""
    coordinator: BicWrgCoordinator = hass.data[DOMAIN][entry.entry_id]
    
    async_add_entities([BicWrgOperationModeSelect(coordinator, entry)])


class BicWrgOperationModeSelect(CoordinatorEntity[BicWrgCoordinator], SelectEntity):
    """Select entity for WRG operation mode (Betriebsart)."""

    _attr_has_entity_name = True
    _attr_name = "Operation Mode"
    _attr_options = list(OPERATION_MODES.values())

    def __init__(
        self,
        coordinator: BicWrgCoordinator,
        entry: ConfigEntry,
    ) -> None:
        """Initialize the select entity."""
        super().__init__(coordinator)
        self._attr_unique_id = f"{entry.entry_id}_operation_mode"
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, entry.entry_id)},
            name="WRG 134-BP-HK",
            manufacturer=MANUFACTURER,
            model=MODEL,
        )

    @property
    def current_option(self) -> str | None:
        """Return the current operation mode."""
        mode = self.coordinator.data.get("operation_mode")
        if mode is not None and mode in OPERATION_MODES:
            return OPERATION_MODES[mode]
        return None

    async def async_select_option(self, option: str) -> None:
        """Change the operation mode."""
        # Find the mode value for the selected option
        mode_value = None
        for value, name in OPERATION_MODES.items():
            if name == option:
                mode_value = value
                break
        
        if mode_value is None:
            return
        
        # Write to device
        success = await self.hass.async_add_executor_job(
            self.coordinator.client.write_operation_mode, mode_value
        )
        
        if success:
            # Update coordinator data immediately
            await self.coordinator.async_request_refresh()
