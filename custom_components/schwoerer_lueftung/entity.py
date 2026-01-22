"""Base entity for Schwörer Lüftung."""
from __future__ import annotations

from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .coordinator import Coordinator


class Entity(CoordinatorEntity[Coordinator]):
    """Base entity for Schwörer Lüftung."""

    def __init__(self, coordinator: Coordinator) -> None:
        """Initialize the entity."""
        super().__init__(coordinator)
        self._attr_device_info = coordinator.get_device()
