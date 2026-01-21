"""Select platform for BIC WRG."""
from __future__ import annotations

from homeassistant.components.select import SelectEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity import DeviceInfo
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN, MANUFACTURER, MODEL_WGT, MODEL_WRT
from .coordinator import Coordinator
from .modbus_client import (
    OPERATION_MODE_OFF,
    OPERATION_MODE_MANUAL,
    OPERATION_MODE_WINTER,
    OPERATION_MODE_SUMMER,
    OPERATION_MODE_SUMMER_EXHAUST,
    FAN_SPEED_OFF,
    FAN_SPEED_LEVEL_1,
    FAN_SPEED_LEVEL_2,
    FAN_SPEED_LEVEL_3,
    FAN_SPEED_LEVEL_4,
    FAN_SPEED_AUTO,
    FAN_SPEED_LINEAR,
    HEATING_COOLING_OFF,
    HEATING_COOLING_HEATING,
    HEATING_COOLING_COOLING,
    HEATING_COOLING_AUTO_OUTDOOR,
    HEATING_COOLING_AUTO_DIGITAL,
    HEAT_PUMP_HEATING_OFF,
    HEAT_PUMP_HEATING_ENABLED,
    HEAT_PUMP_COOLING_OFF,
    HEAT_PUMP_COOLING_ENABLED,
    AUXILIARY_HEATING_OFF,
    AUXILIARY_HEATING_ENABLED,
)

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
        OperationModeSelect(coordinator, entry),
        FanSpeedSelect(coordinator, entry),
    ]
    
    # Add heating-related select entities only for WGT devices
    if has_heating:
        entities.append(HeatingCoolingFunctionSelect(coordinator, entry))
    
    async_add_entities(entities)


class OperationModeSelect(CoordinatorEntity[Coordinator], SelectEntity):
    """Select entity for WRG operation mode (Betriebsart)."""

    _attr_has_entity_name = True
    _attr_translation_key = "operation_mode"
    _attr_options = list(OPERATION_MODES.values())

    def __init__(
        self,
        coordinator: Coordinator,
        entry: ConfigEntry,
    ) -> None:
        """Initialize the select entity."""
        super().__init__(coordinator)
        self._attr_unique_id = f"{entry.entry_id}_operation_mode"
        model = MODEL_WGT if coordinator.has_heating() else MODEL_WRT
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, entry.entry_id)},
            name="Lüftung",
            manufacturer=MANUFACTURER,
            model=model,
        )

    @property
    def current_option(self) -> str | None:
        """Return the current operation mode."""
        mode = self.coordinator.data.get("operation_mode")
        if mode is not None and mode in OPERATION_MODES:
            return OPERATION_MODES[mode]
        return None

    async def async_select_option(self, option: str) -> None:
        """Change the operation mode."""
        # Find the mode value for the selected option
        mode_value = None
        for value, name in OPERATION_MODES.items():
            if name == option:
                mode_value = value
                break
        
        if mode_value is None:
            return
        
        # Write to device
        success = await self.hass.async_add_executor_job(
            self.coordinator.client.write_operation_mode, mode_value
        )
        
        if success:
            # Update coordinator data immediately
            await self.coordinator.async_request_refresh()


class FanSpeedSelect(CoordinatorEntity[Coordinator], SelectEntity):
    """Select entity for WRG fan speed (Manuelle Luftstufe)."""

    _attr_has_entity_name = True
    _attr_translation_key = "manual_fan_level"
    _attr_options = list(FAN_SPEEDS.values())

    def __init__(
        self,
        coordinator: Coordinator,
        entry: ConfigEntry,
    ) -> None:
        """Initialize the select entity."""
        super().__init__(coordinator)
        self._attr_unique_id = f"{entry.entry_id}_fan_speed"
        model = MODEL_WGT if coordinator.has_heating() else MODEL_WRT
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, entry.entry_id)},
            name="Lüftung",
            manufacturer=MANUFACTURER,
            model=model,
        )

    @property
    def current_option(self) -> str | None:
        """Return the current fan speed."""
        speed = self.coordinator.data.get("fan_speed")
        if speed is not None and speed in FAN_SPEEDS:
            return FAN_SPEEDS[speed]
        return None

    async def async_select_option(self, option: str) -> None:
        """Change the fan speed."""
        # Find the speed value for the selected option
        speed_value = None
        for value, name in FAN_SPEEDS.items():
            if name == option:
                speed_value = value
                break
        
        if speed_value is None:
            return
        
        # Write to device
        success = await self.hass.async_add_executor_job(
            self.coordinator.client.write_fan_speed, speed_value
        )
        
        if success:
            # Update coordinator data immediately
            await self.coordinator.async_request_refresh()


class HeatingCoolingFunctionSelect(CoordinatorEntity[Coordinator], SelectEntity):
    """Select entity for WRG heating/cooling function (Heiz-Kühlfunktion)."""

    _attr_has_entity_name = True
    _attr_translation_key = "heating_cooling_function"
    _attr_options = list(HEATING_COOLING_MODES.values())

    def __init__(
        self,
        coordinator: Coordinator,
        entry: ConfigEntry,
    ) -> None:
        """Initialize the select entity."""
        super().__init__(coordinator)
        self._attr_unique_id = f"{entry.entry_id}_heating_cooling_function"
        model = MODEL_WGT if coordinator.has_heating() else MODEL_WRT
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, entry.entry_id)},
            name="Lüftung",
            manufacturer=MANUFACTURER,
            model=model,
        )

    @property
    def current_option(self) -> str | None:
        """Return the current heating/cooling function."""
        mode = self.coordinator.data.get("heating_cooling_function")
        if mode is not None and mode in HEATING_COOLING_MODES:
            return HEATING_COOLING_MODES[mode]
        return None

    async def async_select_option(self, option: str) -> None:
        """Change the heating/cooling function."""
        mode_value = None
        for value, name in HEATING_COOLING_MODES.items():
            if name == option:
                mode_value = value
                break
        
        if mode_value is None:
            return
        
        success = await self.hass.async_add_executor_job(
            self.coordinator.client.write_heating_cooling_function, mode_value
        )
        
        if success:
            await self.coordinator.async_request_refresh()
