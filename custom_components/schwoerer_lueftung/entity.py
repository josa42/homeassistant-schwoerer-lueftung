"""Base entity for Schwörer Lüftung."""
from __future__ import annotations

from homeassistant.helpers.entity import DeviceInfo
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN, MANUFACTURER, MODEL
from .coordinator import BicWrgCoordinator


class BicWrgEntity(CoordinatorEntity[BicWrgCoordinator]):
    """Base entity for Schwörer Lüftung."""

    def __init__(self, coordinator: BicWrgCoordinator) -> None:
        """Initialize the entity."""
        super().__init__(coordinator)
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, coordinator.config_entry.entry_id)},
            name="Schwörer Lüftung",
            manufacturer=MANUFACTURER,
            model=MODEL,
        )
