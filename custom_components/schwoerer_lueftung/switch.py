"""Switch platform for Schwörer Lüftung."""

from __future__ import annotations

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from custom_components.schwoerer_lueftung.abstract import (
    AbstractRoomSwitch,
    AbstractSwitch,
)

from .const import CONF_ROOMS, DOMAIN
from .coordinator import Coordinator
from .modbus.registers import (
    REG_AUXILIARY_HEATING_ENABLED,
    REG_AUXILIARY_HEATING_ENABLED_ROOM_1,
    REG_HEAT_PUMP_COOLING_ENABLED,
    REG_HEAT_PUMP_HEATING_ENABLED,
    REG_SCHEDULED_HEATING_ENABLED_ROOM_1,
    REG_SHOCK_VENTILATION,
)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    coordinator: Coordinator = hass.data[DOMAIN][entry.entry_id]
    has_heating = coordinator.has_heating()

    entities = []
    entities.extend([ShockVentilationSwitch(coordinator)])

    # Add heating-related switches only for WGT devices
    if has_heating:
        entities.extend(
            [
                HeatPumpHeatingSwitch(coordinator),
                HeatPumpCoolingSwitch(coordinator),
                AuxiliaryHeatingSwitch(coordinator),
            ]
        )

        rooms = entry.data.get(CONF_ROOMS, [])
        for room in rooms:
            entities.append(
                RoomAuxiliaryHeatingEnableSwitch(coordinator, room["number"])
            )
            entities.append(
                RoomTimeProgramHeatingEnableSwitch(coordinator, room["number"])
            )

    async_add_entities(entities)


class ShockVentilationSwitch(AbstractSwitch):
    """
    Switch for enabling/disabling shock ventilation.
    (Stoßlüftung)

    Register: 111
    Value:      0: Off
                1: On
    """

    def __init__(self, coordinator: Coordinator) -> None:
        super().__init__(coordinator, REG_SHOCK_VENTILATION)


class HeatPumpHeatingSwitch(AbstractSwitch):
    """
    Switch for enabling/disabling heat pump heating for the whole ventilation system.
    (Wärmepumpe Heizen)

    Register: 231
    Value:      0: Disabled
                1: Enabled
    """

    def __init__(self, coordinator: Coordinator) -> None:
        super().__init__(coordinator, REG_HEAT_PUMP_HEATING_ENABLED)


class HeatPumpCoolingSwitch(AbstractSwitch):
    """
    Switch for enabling/disabling heat pump cooling for the whole ventilation system.
    (Wärmepumpe Kühlen)

    Register: 232
    Value:      0: Disabled
                1: Enabled
    """

    def __init__(self, coordinator: Coordinator) -> None:
        super().__init__(coordinator, REG_HEAT_PUMP_COOLING_ENABLED)


class AuxiliaryHeatingSwitch(AbstractSwitch):
    def __init__(self, coordinator: Coordinator) -> None:
        super().__init__(coordinator, REG_AUXILIARY_HEATING_ENABLED)


class RoomAuxiliaryHeatingEnableSwitch(AbstractRoomSwitch):
    """
    Switch for enabling/disabling auxiliary heating for a specific room.
    (Zusatzheizung Freigabe Raum)

    - Register: 440-456
    - Value:     0: Disabled
                 1: Enabled
    """

    def __init__(self, coordinator: Coordinator, room_number: int) -> None:
        super().__init__(
            coordinator,
            room_number,
            REG_AUXILIARY_HEATING_ENABLED_ROOM_1,
            enabled_by_default=False,
        )


class RoomTimeProgramHeatingEnableSwitch(AbstractRoomSwitch):
    """
    Switch for enabling/disabling time-programmed heating for a specific room.
    (Freigabe Zeitprogramm Heizen Raum)

    - Register: 500-516
    - Value:     0: Disabled
                 1: Enabled
    """

    def __init__(self, coordinator: Coordinator, room_number: int) -> None:
        super().__init__(
            coordinator,
            room_number,
            REG_SCHEDULED_HEATING_ENABLED_ROOM_1,
            enabled_by_default=False,
        )
