"""Base entity for BIC WRG."""
from __future__ import annotations

from homeassistant.helpers.entity import DeviceInfo
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN, MANUFACTURER, MODEL
from .coordinator import BicWrgCoordinator


class BicWrgEntity(CoordinatorEntity[BicWrgCoordinator]):
    """Base entity for BIC WRG."""

    def __init__(self, coordinator: BicWrgCoordinator) -> None:
        """Initialize the entity."""
        super().__init__(coordinator)
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, coordinator.config_entry.entry_id)},
            name="BIC WRG",
            manufacturer=MANUFACTURER,
            model=MODEL,
        )
