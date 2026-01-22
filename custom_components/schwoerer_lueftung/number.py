"""Number platform for BIC WRG."""
from __future__ import annotations

from homeassistant.components.number import NumberMode
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .abstract import AbstarctRoomNumber, AbstractNumber

from .const import DOMAIN, MANUFACTURER, MODEL_WGT, MODEL_WRT
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
    """Set up WRG number entities from a config entry."""
    coordinator: Coordinator = hass.data[DOMAIN][entry.entry_id]

    model = MODEL_WGT if coordinator.has_heating() else MODEL_WRT
    device = DeviceInfo(
        identifiers={(DOMAIN, entry.entry_id)},
        name="Lüftung",
        manufacturer=MANUFACTURER,
        model=model,
    )

    entities = []
    entities.append(LinearFanPowerNumber(coordinator, device))

    # Add base temperature numbers for each configured room (WGT only)
    if coordinator.has_heating():
        rooms = entry.data.get("rooms", [])
        for room in rooms:
            room_device = DeviceInfo(
                identifiers={
                    (DOMAIN, f"{coordinator.config_entry.entry_id}_room_{room["number"]}")
                },
                name=room["name"],
                manufacturer=MANUFACTURER,
                model="Room Climate Control",
                via_device=(DOMAIN, coordinator.config_entry.entry_id),
            )
            entities.append(
                RoomBaseTemperatureNumber(coordinator, room_device, room["number"])
            )

    async_add_entities(entities)




class LinearFanPowerNumber(AbstractNumber):

    def __init__(
        self,
        coordinator: Coordinator,
        device: DeviceInfo
    ) -> None:
        """Initialize the number entity."""
        super().__init__(coordinator, device, REG_LINEAR_FAN_POWER)

        self._attr_translation_key = "linear_fan_power"
        self._attr_native_min_value = LINEAR_FAN_POWER_MIN
        self._attr_native_max_value = LINEAR_FAN_POWER_MAX
        self._attr_native_step = 1
        self._attr_native_unit_of_measurement = "%"
        self._attr_mode = NumberMode.SLIDER
        self._attr_entity_registry_enabled_default = False



class RoomBaseTemperatureNumber(AbstarctRoomNumber):
    def __init__(
        self,
        coordinator: Coordinator,
        device: DeviceInfo,
        room_number: int,
    ) -> None:
        """Initialize the number entity."""
        super().__init__(coordinator, device, room_number, REG_BASE_TEMPERATURE_1)
        self._attr_native_min_value = 10.0
        self._attr_native_max_value = 30.0
        self._attr_native_step = 0.1
        self._attr_native_unit_of_measurement = "°C"
        self._attr_mode = NumberMode.BOX
        self._attr_entity_registry_enabled_default = False

