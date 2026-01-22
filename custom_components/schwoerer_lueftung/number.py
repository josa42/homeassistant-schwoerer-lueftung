from __future__ import annotations

from homeassistant.components.number import NumberMode
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .abstract import AbstarctRoomNumber, AbstractNumber
from .const import DOMAIN
from .coordinator import Coordinator
from .modbus.registers import (
    LINEAR_FAN_POWER_MAX,
    LINEAR_FAN_POWER_MIN,
    REG_BASE_TEMPERATURE_1,
    REG_LINEAR_FAN_POWER,
)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    coordinator: Coordinator = hass.data[DOMAIN][entry.entry_id]

    entities = []
    entities.append(LinearFanPowerNumber(coordinator))

    # Add base temperature numbers for each configured room (WGT only)
    if coordinator.has_heating():
        rooms = entry.data.get("rooms", [])
        for room in rooms:
            entities.append(RoomBaseTemperatureNumber(coordinator, room["number"]))

    async_add_entities(entities)

class LinearFanPowerNumber(AbstractNumber):
    def __init__(self, coordinator: Coordinator) -> None:
        super().__init__(coordinator, REG_LINEAR_FAN_POWER)

        self._attr_translation_key = "linear_fan_power"
        self._attr_native_min_value = LINEAR_FAN_POWER_MIN
        self._attr_native_max_value = LINEAR_FAN_POWER_MAX
        self._attr_native_step = 1
        self._attr_native_unit_of_measurement = "%"
        self._attr_mode = NumberMode.SLIDER
        self._attr_entity_registry_enabled_default = False



class RoomBaseTemperatureNumber(AbstarctRoomNumber):
    def __init__(self, coordinator: Coordinator, room_number: int) -> None:
        super().__init__(coordinator, room_number, REG_BASE_TEMPERATURE_1)

        self._attr_native_min_value = 10.0
        self._attr_native_max_value = 30.0
        self._attr_native_step = 0.1
        self._attr_native_unit_of_measurement = "°C"
        self._attr_mode = NumberMode.BOX
        self._attr_entity_registry_enabled_default = False

