"""Base entity for Schwörer Lüftung."""
from __future__ import annotations

from homeassistant.components.number import NumberMode
from homeassistant.components.sensor import SensorDeviceClass, SensorStateClass
from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from custom_components.schwoerer_lueftung.const import (
    CONF_ENABLE_ALL_SENSORS_BY_DEFAULT,
)
from custom_components.schwoerer_lueftung.modbus.registers import REG_KEYS

from .coordinator import Coordinator


class Entity(CoordinatorEntity[Coordinator]):
    def __init__(
        self,
        coordinator: Coordinator,
        register: int = 0,
        device: DeviceInfo|None = None,
        translation_key: str|None = None,
        device_class: SensorDeviceClass|None = None,
        state_class: SensorStateClass|str|None = None,
        unit_of_measurement: str|None = None,
        enabled_by_default: bool = True,
        precision: int|None = None,
        min_value: float|None = None,
        max_value: float|None = None,
        step: float|None = None,
        mode: NumberMode|None = None,
        unique_id: str|None = None,
        key: str|None = None,
    ) -> None:
        super().__init__(coordinator)

        if key is None:
            key = REG_KEYS.get(register)

        entry = coordinator.config_entry

        self._attr_has_entity_name = True
        self._attr_device_info = device if device is not None else coordinator.get_device()
        self._attr_unique_id = unique_id if unique_id is not None else f"{entry.entry_id}_{key}"
        self._attr_translation_key = translation_key if translation_key is not None else key
        self._register = register

        if device_class is not None:
            self._attr_device_class = device_class
        if state_class is not None:
            self._attr_state_class = state_class
        if unit_of_measurement is not None:
            self._attr_native_unit_of_measurement = unit_of_measurement
        if precision is not None:
            self._attr_suggested_display_precision = precision
        if min_value is not None:
            self._attr_native_min_value = min_value
        if max_value is not None:
            self._attr_native_max_value = max_value
        if step is not None:
            self._attr_native_step = step
        if mode is not None:
            self._attr_mode = mode

        self._attr_entity_registry_enabled_default = enabled_by_default or entry.data.get(
            CONF_ENABLE_ALL_SENSORS_BY_DEFAULT, False
        )


