"""Entity base classes shared by every platform.

An entity names the sub-system it belongs to and the device field it reads.
The sub-system name is also the name the poll's :class:`UpdateReport` uses, so
an entity whose sub-system did not answer goes unavailable while the rest stay
up.

Identity is load-bearing. ``unique_id`` and ``translation_key`` are derived
from ``description.key`` exactly the way the pre-2.0 code derived them from
``REG_KEYS``, so entities keep their history across the upgrade:

- global: ``{entry_id}_{key}``, translation key ``{key}``
- room:   ``{entry_id}_{key}_room_{n}``, translation key ``{key}_room``
"""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass
from typing import TYPE_CHECKING, Any

from homeassistant.helpers.entity import EntityDescription
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import CONF_ENABLE_ALL_SENSORS_BY_DEFAULT
from .coordinator import Coordinator

if TYPE_CHECKING:
    from modbus_connection.model import Component

# The sub-system every room entity reports under. Rooms are polled as one
# component group, so they share a single report name.
ROOMS = "rooms"


@dataclass(frozen=True, kw_only=True)
class SchwoererEntityDescription(EntityDescription):
    """Describe an entity backed by one field of one device sub-system."""

    subsystem: str
    """Attribute on the device, and the name it reports under."""

    field: str | None = None
    """Device field to read and write. Defaults to ``key``."""

    value_fn: Callable[[Any], Any] | None = None
    """Maps the field value to the entity's value. Defaults to identity."""


class SchwoererEntity(CoordinatorEntity[Coordinator]):
    """An entity reading one field off the device."""

    _attr_has_entity_name = True
    entity_description: SchwoererEntityDescription

    def __init__(
        self,
        coordinator: Coordinator,
        description: SchwoererEntityDescription,
        room_number: int | None = None,
    ) -> None:
        super().__init__(coordinator)

        self.entity_description = description
        self._room_number = room_number

        entry = coordinator.config_entry

        if room_number is None:
            self._attr_unique_id = f"{entry.entry_id}_{description.key}"
            self._attr_translation_key = description.key
            self._attr_device_info = coordinator.get_device()
        else:
            self._attr_unique_id = (
                f"{entry.entry_id}_{description.key}_room_{room_number}"
            )
            self._attr_translation_key = f"{description.key}_room"
            self._attr_device_info = coordinator.get_room_device(room_number)

        self._attr_entity_registry_enabled_default = (
            description.entity_registry_enabled_default
            or entry.data.get(CONF_ENABLE_ALL_SENSORS_BY_DEFAULT, False)
        )

    @property
    def _component(self) -> Component | None:
        """The device sub-system this entity reads, if the device has it."""
        if self.entity_description.subsystem == ROOMS:
            assert self._room_number is not None
            return self.coordinator.device.room(self._room_number)
        return getattr(self.coordinator.device, self.entity_description.subsystem)

    @property
    def _field(self) -> str:
        return self.entity_description.field or self.entity_description.key

    @property
    def _value(self) -> Any:
        """The entity's value, or None if the field has not been read."""
        component = self._component
        if component is None:
            return None

        value = getattr(component, self._field)
        if value is None or self.entity_description.value_fn is None:
            return value
        return self.entity_description.value_fn(value)

    @property
    def available(self) -> bool:
        """Available while this entity's own sub-system keeps answering.

        A sub-system the device refuses fails alone, so the entities that do
        not depend on it stay up.
        """
        return (
            super().available
            and self.entity_description.subsystem in self.coordinator.data.updated
        )

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        attributes: dict[str, Any] = {"entity_type": self._attr_translation_key}
        if self._room_number is not None:
            attributes["room_number"] = self._room_number
        return attributes

    async def _async_write(self, value: Any) -> None:
        """Write the entity's field back to the device."""
        component = self._component
        if component is None:
            return
        await self.coordinator.async_write(component, self._field, value)
