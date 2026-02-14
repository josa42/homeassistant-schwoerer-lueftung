from __future__ import annotations

import logging
import re

from homeassistant.components.binary_sensor import BinarySensorEntity
from homeassistant.components.number import NumberEntity, NumberMode
from homeassistant.components.select import SelectEntity
from homeassistant.components.sensor import (
    SensorDeviceClass,
    SensorEntity,
    SensorStateClass,
)
from homeassistant.components.switch import SwitchEntity
from homeassistant.const import UnitOfTemperature
from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from custom_components.schwoerer_lueftung.const import (
    CONF_ENABLE_ALL_SENSORS_BY_DEFAULT,
)
from custom_components.schwoerer_lueftung.modbus.registers import (
    REG_KEYS,
    room_reg,
)
from custom_components.schwoerer_lueftung.modbus.transforms import to_temperature

from .coordinator import Coordinator

_LOGGER = logging.getLogger(__name__)


class Entity(CoordinatorEntity[Coordinator]):
    def __init__(
        self,
        coordinator: Coordinator,
        register: int = 0,
        device: DeviceInfo | None = None,
        entity_type: str | None = None,
        device_class: SensorDeviceClass | None = None,
        state_class: SensorStateClass | str | None = None,
        unit_of_measurement: str | None = None,
        enabled_by_default: bool = True,
        precision: int | None = None,
        min_value: float | None = None,
        max_value: float | None = None,
        step: float | None = None,
        mode: NumberMode | None = None,
        unique_id: str | None = None,
        key: str | None = None,
    ) -> None:
        super().__init__(coordinator)

        if key is None:
            key = REG_KEYS.get(register)

        entry = coordinator.config_entry

        self._attr_has_entity_name = True
        self._attr_device_info = (
            device if device is not None else coordinator.get_device()
        )
        self._attr_unique_id = (
            unique_id if unique_id is not None else f"{entry.entry_id}_{key}"
        )
        self._entity_type = (
            entity_type if entity_type is not None else key
        )
        self._attr_translation_key = self._entity_type
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

        self._attr_entity_registry_enabled_default = (
            enabled_by_default
            or entry.data.get(CONF_ENABLE_ALL_SENSORS_BY_DEFAULT, False)
        )


class AbstractSensor(Entity, SensorEntity):
    def __init__(self, coordinator: Coordinator, register: int, **kwargs) -> None:
        super().__init__(coordinator, register, **kwargs)

    @property
    def native_value(self) -> int | None:
        return self.coordinator.get_data(self._register)

    @property
    def extra_state_attributes(self) -> dict:
        """Return the raw numeric value as an attribute for debugging."""
        return {
            "raw_value": self.coordinator.get_data(self._register),
            "entity_type": self._entity_type,
        }


class AbstractTemperatureSensor(AbstractSensor):
    """Sensor for temperature values that applies temperature transformation."""

    def __init__(self, coordinator: Coordinator, register: int, **kwargs) -> None:
        super().__init__(
            coordinator,
            register,
            device_class=SensorDeviceClass.TEMPERATURE,
            state_class=SensorStateClass.MEASUREMENT,
            unit_of_measurement=UnitOfTemperature.CELSIUS,
            **kwargs,
        )

    @property
    def native_value(self) -> float | None:
        """Return temperature value with transformation applied."""
        raw_value = self.coordinator.get_data(self._register)
        return to_temperature(raw_value)


class AbstractEnumSensor(AbstractSensor):
    """Sensor with enum device class that maps numeric values to string states."""

    def __init__(
        self, coordinator: Coordinator, register: int, options: dict[int, str], **kwargs
    ) -> None:
        super().__init__(
            coordinator, register, device_class=SensorDeviceClass.ENUM, **kwargs
        )

        self._options = options
        self._attr_options = list(options.values())

    @property
    def native_value(self) -> str | None:
        """Return the state mapped to string identifier."""
        raw_value = self.coordinator.get_data(self._register)
        if raw_value is None:
            return None
        return self._options.get(raw_value)


class AbstractRoomSensor(AbstractSensor):
    def __init__(
        self, coordinator: Coordinator, base_register: int, room_number: int, **kwargs
    ) -> None:
        register = room_reg(base_register, room_number)
        entity_type = (
            kwargs.pop("entity_type", None)
            or re.sub(r"_\d+$", "", REG_KEYS.get(register) or "")
            or ""
        )

        super().__init__(
            coordinator,
            room_reg(base_register, room_number),
            device=coordinator.get_room_device(room_number),
            entity_type=entity_type,
            **kwargs,
        )


class AbstractRoomTemperatureSensor(AbstractRoomSensor):
    """Room temperature sensor that applies temperature transformation."""

    def __init__(
        self, coordinator: Coordinator, base_register: int, room_number: int, **kwargs
    ) -> None:
        super().__init__(
            coordinator,
            base_register,
            room_number,
            device_class=SensorDeviceClass.TEMPERATURE,
            state_class=SensorStateClass.MEASUREMENT,
            unit_of_measurement=UnitOfTemperature.CELSIUS,
            **kwargs,
        )

        self._room_number = room_number
        self._base_register = base_register

    @property
    def native_value(self) -> float | None:
        """Return temperature value with transformation applied."""
        raw_value = self.coordinator.get_room_data(
            self._base_register, self._room_number
        )
        return to_temperature(raw_value)


class AbstractBinarySensor(Entity, BinarySensorEntity):
    """Binary sensor that handles transformation from raw register values to boolean state."""

    def __init__(
        self,
        coordinator: Coordinator,
        register: int,
        active_states: set[int] = {1},
        **kwargs,
    ) -> None:
        super().__init__(coordinator, register, **kwargs)

        self._active_states = active_states

    @property
    def is_on(self) -> bool | None:
        value = self.coordinator.get_data(self._register)

        if value is None:
            return None

        # Check if value is in the set of active states
        return value in self._active_states

    @property
    def extra_state_attributes(self) -> dict:
        """Return the sensor type as an attribute."""
        return {"entity_type": self._entity_type}


class AbstractBinaryRoomSensor(AbstractBinarySensor):
    def __init__(
        self,
        coordinator: Coordinator,
        base_register: int,
        room_number: int,
        active_states: set[int] = {1},
        **kwargs,
    ) -> None:
        register = room_reg(base_register, room_number)
        super().__init__(
            coordinator,
            register,
            active_states,
            device=coordinator.get_room_device(room_number),
            entity_type=re.sub(r"_\d+$", "", REG_KEYS.get(register) or "") or "",
            **kwargs,
        )


class AbstractSelect(Entity, SelectEntity):
    def __init__(
        self, coordinator: Coordinator, register: int, options: dict[int, str], **kwargs
    ) -> None:
        super().__init__(coordinator, register, **kwargs)

        self._options = options
        self._attr_options = list(options.values())

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

    @property
    def extra_state_attributes(self) -> dict:
        """Return the sensor type as an attribute."""
        return {"entity_type": self._entity_type}


class AbstractNumber(Entity, NumberEntity):
    def __init__(self, coordinator: Coordinator, register: int, **kwargs) -> None:
        super().__init__(coordinator, register, **kwargs)

    @property
    def native_value(self) -> float | None:
        return self.coordinator.get_data(self._register)

    async def async_set_native_value(self, value: float) -> None:
        await self.coordinator.async_write_register(self._register, int(value))

    @property
    def extra_state_attributes(self) -> dict:
        """Return the sensor type as an attribute."""
        return {"entity_type": self._entity_type}


class AbstractRoomNumber(AbstractNumber):
    def __init__(
        self, coordinator: Coordinator, room_number: int, base_register: int, **kwargs
    ) -> None:
        register = room_reg(base_register, room_number)
        super().__init__(
            coordinator,
            register,
            device=coordinator.get_room_device(room_number),
            entity_type=re.sub(r"_\d+$", "", REG_KEYS.get(register) or "") or "",
            **kwargs,
        )


class AbstractSwitch(Entity, SwitchEntity):
    def __init__(self, coordinator: Coordinator, register: int, **kwargs) -> None:
        super().__init__(coordinator, register, **kwargs)

    @property
    def is_on(self) -> bool | None:
        value = self.coordinator.get_data(self._register)
        return value == 1 if value is not None else None

    async def async_turn_on(self) -> None:
        await self.coordinator.async_write_register(self._register, 1)

    async def async_turn_off(self) -> None:
        await self.coordinator.async_write_register(self._register, 0)

    @property
    def extra_state_attributes(self) -> dict:
        """Return the sensor type as an attribute."""
        return {"entity_type": self._entity_type}


class AbstractRoomSwitch(AbstractSwitch):
    def __init__(
        self, coordinator: Coordinator, room_number: int, base_register: int, **kwargs
    ) -> None:
        register = room_reg(base_register, room_number)
        super().__init__(
            coordinator,
            register,
            device=coordinator.get_room_device(room_number),
            entity_type=re.sub(r"_\d+$", "", REG_KEYS.get(register) or "") or "",
            **kwargs,
        )
