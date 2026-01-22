"""Base entity for Schwörer Lüftung."""
from __future__ import annotations

from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .coordinator import Coordinator


class Entity(CoordinatorEntity[Coordinator]):
    def __init__(self, coordinator: Coordinator) -> None:
        super().__init__(coordinator)
        self._attr_device_info = coordinator.get_device()
