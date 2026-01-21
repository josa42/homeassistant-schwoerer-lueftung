"""Base entity for Schwörer Lüftung."""
from __future__ import annotations

from homeassistant.helpers.entity import DeviceInfo
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN, MANUFACTURER, MODEL_WGT, MODEL_WRT
from .coordinator import BicWrgCoordinator


class BicWrgEntity(CoordinatorEntity[BicWrgCoordinator]):
    """Base entity for Schwörer Lüftung."""

    def __init__(self, coordinator: BicWrgCoordinator) -> None:
        """Initialize the entity."""
        super().__init__(coordinator)
        # Set device name and model based on device type
        if coordinator.has_heating():
            device_name = "Schwörer Heizung"
            model = MODEL_WGT
        else:
            device_name = "Schwörer Lüftung"
            model = MODEL_WRT
        
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, coordinator.config_entry.entry_id)},
            name=device_name,
            manufacturer=MANUFACTURER,
            model=model,
        )
