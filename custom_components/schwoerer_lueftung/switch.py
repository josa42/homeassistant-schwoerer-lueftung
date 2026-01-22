"""Switch platform for BIC WRG."""
from __future__ import annotations

import logging

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from custom_components.schwoerer_lueftung.abstract import AbstractSwitch,AbstractRoomSwitch

from .const import DOMAIN, MANUFACTURER, MODEL_WGT, MODEL_WRT
from .coordinator import Coordinator
from .modbus.registers import (
    REG_AUXILIARY_HEATING_ENABLED,
    REG_HEAT_PUMP_COOLING_ENABLED,
    REG_HEAT_PUMP_HEATING_ENABLED,
    REG_AUXILIARY_HEATING_ENABLED_ROOM_1,
    REG_SCHEDULED_HEATING_ENABLED_1,
    REG_SHOCK_VENTILATION,
)

_LOGGER = logging.getLogger(__name__)

async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up WRG switch entities from a config entry."""
    coordinator: Coordinator = hass.data[DOMAIN][entry.entry_id]
    has_heating = coordinator.has_heating()

    model = MODEL_WGT if coordinator.has_heating() else MODEL_WRT
    device = DeviceInfo(
        identifiers={(DOMAIN, coordinator.config_entry.entry_id)},
        name="Lüftung",
        manufacturer=MANUFACTURER,
        model=model,
    )


    entities = []
    entities.extend([ ShockVentilationSwitch(coordinator)])

    # Add heating-related switches only for WGT devices
    if has_heating:
        entities.extend([
            HeatPumpHeatingSwitch(coordinator),
            HeatPumpCoolingSwitch(coordinator),
            AuxiliaryHeatingSwitch(coordinator),
        ])

    # Add room heating switches (only for WGT)
    if has_heating:
        rooms = entry.data.get("rooms", [])
        for room in rooms:
            entities.append(RoomAuxiliaryHeatingEnableSwitch(coordinator, room["number"]))
            entities.append(RoomTimeProgramHeatingEnableSwitch(coordinator, room["number"])
            )

    async_add_entities(entities)


class ShockVentilationSwitch(AbstractSwitch):
    """Switch entity for WRG shock ventilation (Stoßlüftung)."""

    def __init__(self, coordinator: Coordinator) -> None:
        super().__init__(coordinator, REG_SHOCK_VENTILATION)


class RoomAuxiliaryHeatingEnableSwitch(AbstractRoomSwitch):
    """Switch entity for room auxiliary heating enable (Zusatzheizung Freigabe)."""

    _attr_entity_registry_enabled_default = False

    def __init__(self, coordinator: Coordinator, room_number: int) -> None:
        super().__init__(coordinator, room_number, REG_AUXILIARY_HEATING_ENABLED_ROOM_1)

class RoomTimeProgramHeatingEnableSwitch(AbstractRoomSwitch):
    """Switch entity for room time program heating enable.

    Freigabe Zeitprogramm Heizen.
    """

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

