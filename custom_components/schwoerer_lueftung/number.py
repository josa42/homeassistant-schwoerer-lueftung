from __future__ import annotations

from homeassistant.components.number import NumberMode
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import TEMPERATURE, UnitOfTemperature
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .abstract import AbstractNumber, AbstractRoomNumber
from .const import DOMAIN
from .coordinator import Coordinator
from .modbus.registers import (
    LINEAR_FAN_POWER_MAX,
    LINEAR_FAN_POWER_MIN,
    REG_BASE_TEMPERATURE_ROOM_1,
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
    """
    Conrol for linear fan power setting.
    (Manuelle Lineare Luftleistung)

    Register: 103
    Value:    30-100 (%)
    """
    def __init__(self, coordinator: Coordinator) -> None:
        super().__init__(
            coordinator,
            REG_LINEAR_FAN_POWER,
            min_value=LINEAR_FAN_POWER_MIN,
            max_value=LINEAR_FAN_POWER_MAX,
            step=1,
            unit_of_measurement="%",
            enabled_by_default=False,
        )

class RoomBaseTemperatureNumber(AbstractRoomNumber):
    """
    Control for room base temperature setting.
    (Grundtemperatur Raum)

    Register: 420-436
    Value:    10.0-30.0 (°C)
    """
    def __init__(self, coordinator: Coordinator, room_number: int) -> None:
        super().__init__(
            coordinator,
            room_number,
            REG_BASE_TEMPERATURE_ROOM_1,
            device_class=TEMPERATURE,
            enabled_by_default=False,
            unit_of_measurement=UnitOfTemperature.CELSIUS,
            min_value=10.0,
            max_value=30.0,
            step=0.1,
            mode=NumberMode.BOX,
        )
