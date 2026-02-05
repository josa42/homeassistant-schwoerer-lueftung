"""Select platform for Schwörer Lüftung."""

from __future__ import annotations

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .abstract import AbstractSelect
from .const import DOMAIN
from .coordinator import Coordinator
from .modbus.registers import (
    REG_FAN_SPEED,
    REG_HEATING_COOLING_FUNCTION,
    REG_OPERATION_MODE,
)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    coordinator: Coordinator = hass.data[DOMAIN][entry.entry_id]
    has_heating = coordinator.has_heating()

    entities = [
        OperationModeSelect(coordinator),
        FanSpeedSelect(coordinator),
    ]

    if has_heating:
        entities.append(HeatingCoolingFunctionSelect(coordinator))

    async_add_entities(entities)


class OperationModeSelect(AbstractSelect):
    """
    Select entity for operation mode.
    (Betriebsart; 0=Aus, 1=Handbetrieb, 2=Winterbetrieb, 3=Sommerbetrieb, 4=Sommer Abluft)

    Registers: 100
    Value:     0-4
    """

    def __init__(
        self,
        coordinator: Coordinator,
    ) -> None:
        super().__init__(
            coordinator,
            REG_OPERATION_MODE,
            {
                0: "off",
                1: "manual",
                2: "winter",
                3: "summer",
                4: "summer_exhaust",
            },
        )


class FanSpeedSelect(AbstractSelect):
    """
    Select entity for fan speed.
    (Manuelle Luftstufe: 0=Aus, 1=Stufe 1, 2=Stufe 2, 3=Stufe 3, 4=Stufe 4, 5=Automatik, 6=Linearbetrieb)

    Registers: 101
    Value:     0-6
    """

    def __init__(
        self,
        coordinator: Coordinator,
    ) -> None:
        super().__init__(
            coordinator,
            REG_FAN_SPEED,
            {
                0: "0",
                1: "1",
                2: "2",
                3: "3",
                4: "4",
                5: "automatic",
                6: "linear",
            },
        )


class HeatingCoolingFunctionSelect(AbstractSelect):
    """
    Select entity for heating/cooling function.
    (Heiz-Kühlfunktion: 0=Aus, 1=Heizen, 2=Kühlen, 3=Auto T-Aussen, 4=Auto Digitaler Eingang)
    """

    def __init__(
        self,
        coordinator: Coordinator,
    ) -> None:
        super().__init__(
            coordinator,
            REG_HEATING_COOLING_FUNCTION,
            {
                0: "off",
                1: "heating",
                2: "cooling",
                3: "auto_outdoor_temp",
                4: "auto_digital_input",
            },
        )
