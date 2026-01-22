from homeassistant.components.binary_sensor import BinarySensorEntity
from custom_components.schwoerer_lueftung.modbus.registers import REG_KEYS
from .coordinator import Coordinator
from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.helpers.update_coordinator import CoordinatorEntity
from homeassistant.components.sensor import (
    SensorEntity,
    SensorStateClass,
)

import re

class AbstractSensor(CoordinatorEntity[Coordinator], SensorEntity):
    _attr_has_entity_name = True
    _attr_state_class = SensorStateClass.MEASUREMENT

    _register: int

    def __init__(
        self,
        coordinator: Coordinator,
        device: DeviceInfo,
        register: int,
    ) -> None:
        super().__init__(coordinator)

        key = REG_KEYS.get(register)
        entry = coordinator.config_entry

        self._attr_device_info = device
        self._attr_unique_id = f"{entry.entry_id}_{key}"
        self._attr_translation_key = key
        self._register = register

    @property
    def native_value(self) -> int | None:
        return self.coordinator.getData(self._register)

class AbstarctRoomSensor(AbstractSensor):
    def __init__(self, coordinator: Coordinator, device: DeviceInfo, room_number: int, base_register: int) -> None:
        super().__init__(coordinator, device, base_register + (room_number - 1))
        self._attr_translation_key = re.sub(r'_\d+$', '',  self._attr_translation_key or '') or ''



class AbstractBinarySensor(CoordinatorEntity[Coordinator], BinarySensorEntity):
    _attr_has_entity_name = True

    def __init__(
        self,
        coordinator: Coordinator,
        device: DeviceInfo,
        register: int,
        active_states: set[int]|None = None,
    ) -> None:
        super().__init__(coordinator)

        key = REG_KEYS.get(register)
        entry = coordinator.config_entry

        self._attr_device_info = device
        self._attr_unique_id = f"{entry.entry_id}_{key}"
        self._attr_translation_key = key
        self._register = register
        self._active_states = active_states

    @property
    def is_on(self) -> bool | None:
        value = self.coordinator.getData(self._register)

        if self._active_states is None:
            return value

        if value is not None:
            return value in self._active_states

        return None

class AbstarctBinaryRoomSensor(AbstractBinarySensor):
    def __init__(
        self,
        coordinator: Coordinator,
        device: DeviceInfo,
        room_number: int,
        base_register: int,
        active_states: set[int]|None = None,
    ) -> None:
        super().__init__(coordinator, device, base_register + (room_number - 1), active_states)
        self._attr_translation_key = re.sub(r'_\d+$', '',  self._attr_translation_key or '') or ''

