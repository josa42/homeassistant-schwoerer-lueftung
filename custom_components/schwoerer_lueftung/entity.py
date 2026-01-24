"""Base entity for Schwörer Lüftung."""
from __future__ import annotations

from homeassistant.components.sensor import SensorDeviceClass, SensorStateClass
from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.helpers.update_coordinator import CoordinatorEntity

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
    ) -> None:
        super().__init__(coordinator)

        key = REG_KEYS.get(register)

        self._attr_has_entity_name = True
        self._attr_device_info = device if device is not None else coordinator.get_device()
        self._attr_unique_id = f"{coordinator.config_entry.entry_id}_{key}"
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

        # if state_class is None:
        #     self._attr_state_class = SensorStateClass.MEASUREMENT

        self._attr_entity_registry_enabled_default = enabled_by_default or True


