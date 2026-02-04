import logging
import re

from homeassistant.components.binary_sensor import BinarySensorEntity
from homeassistant.components.number import NumberEntity
from homeassistant.components.select import SelectEntity
from homeassistant.components.sensor import (
    SensorDeviceClass,
    SensorEntity,
    SensorStateClass,
)
from homeassistant.components.switch import SwitchEntity
from homeassistant.const import UnitOfTemperature

from custom_components.schwoerer_lueftung.entity import Entity
from custom_components.schwoerer_lueftung.modbus.registers import (
    REG_KEYS,
    room_reg,
)
from custom_components.schwoerer_lueftung.modbus.transforms import to_temperature

from .coordinator import Coordinator

_LOGGER = logging.getLogger(__name__)

class AbstractSensor(Entity, SensorEntity):
    def __init__(
        self,
        coordinator: Coordinator,
        register: int,
        **kwargs
    ) -> None:
        super().__init__(
            coordinator,
            register,
            **kwargs
        )

    @property
    def native_value(self) -> int | None:
        return self.coordinator.get_data(self._register)

    @property
    def extra_state_attributes(self) -> dict:
        """Return the raw numeric value as an attribute for debugging."""
        return {
            "raw_value": self.coordinator.get_data(self._register)
        }

class AbstractTemperatureSensor(AbstractSensor):
    """Sensor for temperature values that applies temperature transformation."""
    def __init__(
        self,
        coordinator: Coordinator,
        register: int,
        **kwargs
    ) -> None:
        super().__init__(
            coordinator,
            register,
            device_class=SensorDeviceClass.TEMPERATURE,
            state_class=SensorStateClass.MEASUREMENT,
            unit_of_measurement=UnitOfTemperature.CELSIUS,
            **kwargs
        )

    @property
    def native_value(self) -> float | None:
        """Return temperature value with transformation applied."""
        raw_value = self.coordinator.get_data(self._register)
        return to_temperature(raw_value)

class AbstractEnumSensor(AbstractSensor):
    """Sensor with enum device class that maps numeric values to string states."""
    def __init__(
        self,
        coordinator: Coordinator,
        register: int,
        options: dict[int, str],
        **kwargs
    ) -> None:
        super().__init__(
            coordinator,
            register,
            device_class=SensorDeviceClass.ENUM,
            **kwargs
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
        self, coordinator: Coordinator,
        base_register: int,
        room_number: int,
        **kwargs
    ) -> None:
        register = room_reg(base_register, room_number)
        translation_key = kwargs.pop(
            'translation_key', None
        ) or re.sub(r'_\d+$', '', REG_KEYS.get(register) or '') or ''

        super().__init__(
            coordinator,
            room_reg(base_register, room_number),
            device=coordinator.get_room_device(room_number),
            translation_key=translation_key,
            **kwargs
        )

class AbstractRoomTemperatureSensor(AbstractRoomSensor):
    """Room temperature sensor that applies temperature transformation."""
    def __init__(
        self,
        coordinator: Coordinator,
        base_register: int,
        room_number: int,
        **kwargs
    ) -> None:
        super().__init__(
            coordinator,
            base_register,
            room_number,
            device_class=SensorDeviceClass.TEMPERATURE,
            state_class=SensorStateClass.MEASUREMENT,
            unit_of_measurement=UnitOfTemperature.CELSIUS,
            **kwargs
        )
        
        self._room_number = room_number
        self._base_register = base_register

    @property
    def native_value(self) -> float | None:
        """Return temperature value with transformation applied."""
        raw_value = self.coordinator.get_room_data(self._base_register, self._room_number)
        return to_temperature(raw_value)

class AbstractBinarySensor(Entity, BinarySensorEntity):
    """Binary sensor that handles transformation from raw register values to boolean state."""
    def __init__(
        self,
        coordinator: Coordinator,
        register: int,
        active_states: set[int] = {1},
        **kwargs
    ) -> None:
        super().__init__(
            coordinator,
            register,
            **kwargs
        )

        self._active_states = active_states

    @property
    def is_on(self) -> bool | None:
        value = self.coordinator.get_data(self._register)

        if value is None:
            return None

        # Check if value is in the set of active states
        return value in self._active_states

class AbstractBinaryRoomSensor(AbstractBinarySensor):
    def __init__(
        self,
        coordinator: Coordinator,
        base_register: int,
        room_number: int,
        active_states: set[int] = {1},
        **kwargs
    ) -> None:
        register = room_reg(base_register, room_number)
        super().__init__(
            coordinator,
            register,
            active_states,
            device=coordinator.get_room_device(room_number),
            translation_key=re.sub(r'_\d+$', '', REG_KEYS.get(register) or '') or '',
            **kwargs
        )

class AbstractSelect(Entity, SelectEntity):
    def __init__(
        self,
        coordinator: Coordinator,
        register: int,
        options: dict[int, str],
        **kwargs
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

class AbstractNumber(Entity, NumberEntity):
    def __init__(
        self,
        coordinator: Coordinator,
        register: int,
        **kwargs
    ) -> None:
        super().__init__(coordinator, register, **kwargs)

    @property
    def native_value(self) -> float | None:
        return self.coordinator.get_data(self._register)

    async def async_set_native_value(self, value: float) -> None:
        await self.coordinator.async_write_register(self._register, int(value))

class AbstractRoomNumber(AbstractNumber):
    def __init__(
        self,
        coordinator: Coordinator,
        room_number: int,
        base_register: int,
        **kwargs
    ) -> None:
        register = room_reg(base_register, room_number)
        super().__init__(
            coordinator,
            register,
            device=coordinator.get_room_device(room_number),
            translation_key = re.sub(r'_\d+$', '', REG_KEYS.get(register) or '') or '',
            **kwargs,
        )

class AbstractSwitch(Entity, SwitchEntity):
    def __init__(
        self,
        coordinator: Coordinator,
        register: int,
        **kwargs
    ) -> None:
        super().__init__(coordinator, register, **kwargs)

    @property
    def is_on(self) -> bool | None:
        value = self.coordinator.get_data(self._register)
        return value == 1 if value is not None else None

    async def async_turn_on(self) -> None:
        await self.coordinator.async_write_register(self._register, 1)

    async def async_turn_off(self) -> None:
        await self.coordinator.async_write_register(self._register, 0)

class AbstractRoomSwitch(AbstractSwitch):
    def __init__(
        self,
        coordinator: Coordinator,
        room_number: int,
        base_register: int,
        **kwargs
    ) -> None:
        register = room_reg(base_register, room_number)
        super().__init__(
            coordinator,
            register,
            device=coordinator.get_room_device(room_number),
            translation_key = re.sub(r'_\d+$', '',  REG_KEYS.get(register) or '') or '',
            **kwargs
        )

