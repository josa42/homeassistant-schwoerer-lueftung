from __future__ import annotations

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .abstract import AbstractSelect

from .const import DOMAIN
from .coordinator import Coordinator
from .modbus.registers import (
    AUXILIARY_HEATING_ENABLED,
    AUXILIARY_HEATING_OFF,
    FAN_SPEED_AUTO,
    FAN_SPEED_LEVEL_1,
    FAN_SPEED_LEVEL_2,
    FAN_SPEED_LEVEL_3,
    FAN_SPEED_LEVEL_4,
    FAN_SPEED_LINEAR,
    FAN_SPEED_OFF,
    HEAT_PUMP_COOLING_ENABLED,
    HEAT_PUMP_COOLING_OFF,
    HEAT_PUMP_HEATING_ENABLED,
    HEAT_PUMP_HEATING_OFF,
    HEATING_COOLING_AUTO_DIGITAL,
    HEATING_COOLING_AUTO_OUTDOOR,
    HEATING_COOLING_COOLING,
    HEATING_COOLING_HEATING,
    HEATING_COOLING_OFF,
    OPERATION_MODE_MANUAL,
    OPERATION_MODE_OFF,
    OPERATION_MODE_SUMMER,
    OPERATION_MODE_SUMMER_EXHAUST,
    OPERATION_MODE_WINTER,
    REG_FAN_SPEED,
    REG_HEATING_COOLING_FUNCTION,
    REG_OPERATION_MODE,
)

  # TODO clean up unused mappings

# Operation mode mapping
# Betriebsart: 0=Aus, 1=Handbetrieb, 2=Winterbetrieb, 3=Sommerbetrieb, 4=Sommer Abluft
OPERATION_MODES = {
    OPERATION_MODE_OFF: "off",
    OPERATION_MODE_MANUAL: "manual",
    OPERATION_MODE_WINTER: "winter",
    OPERATION_MODE_SUMMER: "summer",
    OPERATION_MODE_SUMMER_EXHAUST: "summer_exhaust",
}

# Fan speed mapping
# Manuelle Luftstufe: 0=Aus, 1=Stufe 1, 2=Stufe 2, 3=Stufe 3, 4=Stufe 4, 5=Automatik, 6=Linearbetrieb
FAN_SPEEDS = {
    FAN_SPEED_OFF: "0",
    FAN_SPEED_LEVEL_1: "1",
    FAN_SPEED_LEVEL_2: "2",
    FAN_SPEED_LEVEL_3: "3",
    FAN_SPEED_LEVEL_4: "4",
    FAN_SPEED_AUTO: "automatic",
    FAN_SPEED_LINEAR: "linear",
}

# Heating/Cooling function mapping
# Heiz-Kühlfunktion: 0=Aus, 1=Heizen, 2=Kühlen, 3=Auto T-Aussen, 4=Auto Digitaler Eingang
HEATING_COOLING_MODES = {
    HEATING_COOLING_OFF: "off",
    HEATING_COOLING_HEATING: "heating",
    HEATING_COOLING_COOLING: "cooling",
    HEATING_COOLING_AUTO_OUTDOOR: "auto_outdoor_temp",
    HEATING_COOLING_AUTO_DIGITAL: "auto_digital_input",
}

# Heat pump heating enable mapping
# Wärmepumpe Heizen: 0=Heizen Aus, 1=Heizen frei
HEAT_PUMP_HEATING_OPTIONS = {
    HEAT_PUMP_HEATING_OFF: "heating_off",
    HEAT_PUMP_HEATING_ENABLED: "heating_enabled",
}

# Heat pump cooling enable mapping
# Wärmepumpe Kühlen: 0=Kühlen Aus, 1=Kühlen frei
HEAT_PUMP_COOLING_OPTIONS = {
    HEAT_PUMP_COOLING_OFF: "cooling_off",
    HEAT_PUMP_COOLING_ENABLED: "cooling_enabled",
}

# Auxiliary heating enable mapping
# Zusatzheizung Haus: 0=Aus, 1=ZH Haus frei
AUXILIARY_HEATING_OPTIONS = {
    AUXILIARY_HEATING_OFF: "off",
    AUXILIARY_HEATING_ENABLED: "enabled",
}


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up WRG select entities from a config entry."""
    coordinator: Coordinator = hass.data[DOMAIN][entry.entry_id]
    has_heating = coordinator.has_heating()
    entities = [
        OperationModeSelect(coordinator),
        FanSpeedSelect(coordinator),
    ]

    # Add heating-related select entities only for WGT devices
    if has_heating:
        entities.append(HeatingCoolingFunctionSelect(coordinator))

    async_add_entities(entities)

class OperationModeSelect(AbstractSelect):
    def __init__(
        self,
        coordinator: Coordinator,
    ) -> None:
        super().__init__(coordinator, REG_OPERATION_MODE, OPERATION_MODES)


class FanSpeedSelect(AbstractSelect):
    def __init__(
        self,
        coordinator: Coordinator,
    ) -> None:
        super().__init__(coordinator, REG_FAN_SPEED, FAN_SPEEDS)

class HeatingCoolingFunctionSelect(AbstractSelect):
    def __init__(
        self,
        coordinator: Coordinator,
    ) -> None:
        super().__init__(coordinator, REG_HEATING_COOLING_FUNCTION, HEATING_COOLING_MODES)
