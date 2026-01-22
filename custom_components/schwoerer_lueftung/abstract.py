from typing import Any
from homeassistant.components.binary_sensor import BinarySensorEntity
from homeassistant.components.number import NumberEntity
from homeassistant.components.select import SelectEntity
from homeassistant.components.switch import SwitchEntity
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
        register: int,
        device: DeviceInfo | None = None,
    ) -> None:
        super().__init__(coordinator)

        key = REG_KEYS.get(register)
        entry = coordinator.config_entry

        self._attr_device_info = coordinator.get_device() if device is None else device
        self._attr_unique_id = f"{entry.entry_id}_{key}"
        self._attr_translation_key = key
        self._register = register

    @property
    def native_value(self) -> int | None:
        return self.coordinator.get_data(self._register)

class AbstarctRoomSensor(AbstractSensor):
    def __init__(self, coordinator: Coordinator, room_number: int, base_register: int) -> None:
        super().__init__(coordinator, base_register + (room_number - 1), device=coordinator.get_room_device(room_number))
        self._attr_translation_key = re.sub(r'_\d+$', '',  self._attr_translation_key or '') or ''



class AbstractBinarySensor(CoordinatorEntity[Coordinator], BinarySensorEntity):
    _attr_has_entity_name = True

    def __init__(
        self,
        coordinator: Coordinator,
        register: int,
        active_states: set[int]|None = None,
        device: DeviceInfo | None = None,
    ) -> None:
        super().__init__(coordinator)

        key = REG_KEYS.get(register)
        entry = coordinator.config_entry

        self._attr_device_info = coordinator.get_device() if device is None else device
        self._attr_unique_id = f"{entry.entry_id}_{key}"
        self._attr_translation_key = key
        self._register = register
        self._active_states = active_states

    @property
    def is_on(self) -> bool | None:
        value = self.coordinator.get_data(self._register)

        if self._active_states is None:
            return value

        if value is not None:
            return value in self._active_states

        return None

class AbstarctBinaryRoomSensor(AbstractBinarySensor):
    def __init__(
        self,
        coordinator: Coordinator,
        room_number: int,
        base_register: int,
        active_states: set[int]|None = None,
    ) -> None:
        super().__init__(coordinator, base_register + (room_number - 1), active_states, device=coordinator.get_room_device(room_number))
        self._attr_translation_key = re.sub(r'_\d+$', '',  self._attr_translation_key or '') or ''

class AbstractSelect(CoordinatorEntity[Coordinator], SelectEntity):
    _attr_has_entity_name = True

    def __init__(
        self,
        coordinator: Coordinator,
        register: int,
        options: dict[int, str],
        device: DeviceInfo | None = None,
    ) -> None:
        super().__init__(coordinator)

        key = REG_KEYS.get(register)
        entry = coordinator.config_entry

        self._attr_device_info = coordinator.get_device() if device is None else device
        self._attr_unique_id = f"{entry.entry_id}_{key}"
        self._attr_translation_key = key
        self._attr_options = list(options.values())

        self._register = register
        self._options = options


    @property
    def current_option(self) -> str | None:
        return self.coordinator.get_data(self._register, self._options)

    async def async_select_option(self, option: str) -> None:
        value = None
        for options_value, name in self._options.items():
            if name == option:
                value = options_value
                break

        if value is None:
            return

        await self.coordinator.async_write_register(self._register, value)

class AbstractNumber(CoordinatorEntity[Coordinator], NumberEntity):

    _attr_has_entity_name = True

    def __init__(
        self,
        coordinator: Coordinator,
        register: int,
        device: DeviceInfo | None = None,
    ) -> None:
        super().__init__(coordinator)

        key = REG_KEYS.get(register)
        entry = coordinator.config_entry

        self._attr_device_info = coordinator.get_device() if device is None else device
        self._attr_unique_id = f"{entry.entry_id}_{key}"
        self._attr_translation_key = key
        self._register = register

    @property
    def native_value(self) -> float | None:
        return self.coordinator.get_data(self._register)

    async def async_set_native_value(self, value: float) -> None:
        await self.coordinator.async_write_register(self._register, int(value))

class AbstarctRoomNumber(AbstractNumber):
    def __init__(self, coordinator: Coordinator, room_number: int, base_register: int) -> None:
        super().__init__(coordinator, base_register + (room_number - 1), device=coordinator.get_room_device(room_number))
        self._attr_translation_key = re.sub(r'_\d+$', '',  self._attr_translation_key or '') or ''

class AbstractSwitch(CoordinatorEntity[Coordinator], SwitchEntity):
    _attr_has_entity_name = True

    def __init__(
        self,
        coordinator: Coordinator,
        register: int,
        active_states: set[int]|None = None,
        device: DeviceInfo | None = None,
    ) -> None:
        super().__init__(coordinator)

        key = REG_KEYS.get(register)
        entry = coordinator.config_entry

        self._attr_device_info = coordinator.get_device() if device is None else device
        self._attr_unique_id = f"{entry.entry_id}_{key}"
        self._attr_translation_key = key
        self._register = register

    @property
    def is_on(self) -> bool | None:
        value = self.coordinator.get_data(self._register)
        return value == 1 if value is not None else None

    async def async_turn_on(self, **kwargs: Any) -> None:
        await self.coordinator.async_write_register(self._register, 1)

    async def async_turn_off(self, **kwargs: Any) -> None:
        await self.coordinator.async_write_register(self._register, 0)

class AbstractRoomSwitch(AbstractSwitch):
    def __init__(self, coordinator: Coordinator, room_number: int, base_register: int) -> None:
        super().__init__(coordinator, base_register + (room_number - 1), device=coordinator.get_room_device(room_number))
        self._attr_translation_key = re.sub(r'_\d+$', '',  self._attr_translation_key or '') or ''

