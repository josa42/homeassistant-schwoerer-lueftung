from __future__ import annotations

import logging

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from custom_components.schwoerer_lueftung.abstract import (
    AbstractRoomSwitch,
    AbstractSwitch,
)

from .const import DOMAIN
from .coordinator import Coordinator
from .modbus.registers import (
    REG_AUXILIARY_HEATING_ENABLED,
    REG_AUXILIARY_HEATING_ENABLED_ROOM_1,
    REG_HEAT_PUMP_COOLING_ENABLED,
    REG_HEAT_PUMP_HEATING_ENABLED,
    REG_SCHEDULED_HEATING_ENABLED_1,
    REG_SHOCK_VENTILATION,
)

_LOGGER = logging.getLogger(__name__)

async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    coordinator: Coordinator = hass.data[DOMAIN][entry.entry_id]
    has_heating = coordinator.has_heating()

    entities = []
    entities.extend([ ShockVentilationSwitch(coordinator)])

    # Add heating-related switches only for WGT devices
    if has_heating:
        entities.extend([
            HeatPumpHeatingSwitch(coordinator),
            HeatPumpCoolingSwitch(coordinator),
            AuxiliaryHeatingSwitch(coordinator),
        ])

        rooms = entry.data.get("rooms", [])
        for room in rooms:
            entities.append(RoomAuxiliaryHeatingEnableSwitch(coordinator, room["number"]))
            entities.append(RoomTimeProgramHeatingEnableSwitch(coordinator, room["number"]))

    async_add_entities(entities)

class ShockVentilationSwitch(AbstractSwitch):
    def __init__(self, coordinator: Coordinator) -> None:
        super().__init__(coordinator, REG_SHOCK_VENTILATION)


class RoomAuxiliaryHeatingEnableSwitch(AbstractRoomSwitch):
    _attr_entity_registry_enabled_default = False

    def __init__(self, coordinator: Coordinator, room_number: int) -> None:
        super().__init__(coordinator, room_number, REG_AUXILIARY_HEATING_ENABLED_ROOM_1)

class RoomTimeProgramHeatingEnableSwitch(AbstractRoomSwitch):
    _attr_entity_registry_enabled_default = False

    def __init__(self, coordinator: Coordinator, room_number: int) -> None:
        super().__init__(coordinator, room_number, REG_SCHEDULED_HEATING_ENABLED_1)

class HeatPumpHeatingSwitch(AbstractSwitch):
    def __init__(self, coordinator: Coordinator) -> None:
        super().__init__(coordinator, REG_HEAT_PUMP_HEATING_ENABLED)

class HeatPumpCoolingSwitch(AbstractSwitch):
    def __init__(self, coordinator: Coordinator) -> None:
        super().__init__(coordinator, REG_HEAT_PUMP_COOLING_ENABLED)

class AuxiliaryHeatingSwitch(AbstractSwitch):
    def __init__(self, coordinator: Coordinator) -> None:
        super().__init__(coordinator, REG_AUXILIARY_HEATING_ENABLED)

