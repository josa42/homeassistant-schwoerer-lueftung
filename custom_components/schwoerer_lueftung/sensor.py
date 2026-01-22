"""Sensor platform"""

from __future__ import annotations

import logging
from typing import Any

from homeassistant.components.sensor import (
    SensorDeviceClass,
    SensorStateClass,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import UnitOfTemperature, UnitOfTime
from homeassistant.core import HomeAssistant
from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .abstract import (AbstractSensor, AbstarctRoomSensor)

from .const import CONF_ROOMS, DOMAIN, MANUFACTURER, MODEL_WGT, MODEL_WRT
from .coordinator import Coordinator
from .modbus.registers import (
    BYPASS_STATE_CLOSED,
    BYPASS_STATE_OPEN_COOLING,
    BYPASS_STATE_OPEN_HEATING,
    EWT_STATE_COOLING,
    EWT_STATE_HEATING,
    EWT_STATE_OFF,
    EXHAUST_AIR_FAN_STATUS_ACTIVE,
    EXHAUST_AIR_FAN_STATUS_DISABLED,
    EXHAUST_AIR_FAN_STATUS_ERROR,
    EXHAUST_AIR_FAN_STATUS_STANDBY,
    EXHAUST_AIR_FAN_STATUS_STARTUP,
    HEAT_PUMP_STATUS_COOLING,
    HEAT_PUMP_STATUS_HEATING,
    HEAT_PUMP_STATUS_OFF,
    OUTDOOR_DAMPER_STATE_CLOSED,
    OUTDOOR_DAMPER_STATE_OPEN,
    REG_BYPASS_STATE,
    REG_CURRENT_EXHAUST_AIR_FLOW,
    REG_CURRENT_EXHAUST_AIR_RPM,
    REG_CURRENT_FAN_LEVEL,
    REG_CURRENT_SUPPLY_AIR_FLOW,
    REG_CURRENT_SUPPLY_AIR_RPM,
    REG_CURRENT_TEMPERATURE_1,
    REG_DEVICE_FILTER_REMAINING,
    REG_ERROR_MESSAGE,
    REG_EWT_STATE,
    REG_EXHAUST_AIR_FAN_STATUS,
    REG_HEAT_PUMP_STATUS,
    REG_AUXILIARY_HEATING_ENABLED_ROOM_1,
    REG_OPERATING_HOURS_AUXILIARY_HEATING_HOUSE,
    REG_OPERATING_HOURS_EWT,
    REG_OPERATING_HOURS_FAN,
    REG_OPERATING_HOURS_FAN_LEVEL_1,
    REG_OPERATING_HOURS_FAN_LEVEL_2,
    REG_OPERATING_HOURS_FAN_LEVEL_3,
    REG_OPERATING_HOURS_FAN_LEVEL_4,
    REG_OPERATING_HOURS_HEAT_PUMP,
    REG_OPERATING_HOURS_HEAT_PUMP_COOLING,
    REG_OPERATING_HOURS_VHR,
    REG_OUTDOOR_DAMPER_STATE,
    REG_SENSOR_FAN_LEVEL,
    REG_SHOCK_VENTILATION_REMAINING,
    REG_SUPPLY_AIR_FAN_STATUS,
    REG_TEMP_T1_AFTER_EWT,
    REG_TEMP_T2_AFTER_VHR,
    REG_TEMP_T3_BEFORE_NE,
    REG_TEMP_T4_AFTER_NE,
    REG_TEMP_T5_EXHAUST_AIR,
    REG_TEMP_T6_IN_WT,
    REG_TEMP_T7_EVAPORATOR,
    REG_TEMP_T8_CONDENSER,
    REG_TEMP_T10_OUTDOOR,
    REG_TIME_PROGRAM_BASE_LEVEL,
    REG_TIME_PROGRAM_FAN_LEVEL,
    REG_UPSTREAM_FILTER_REMAINING,
    SUPPLY_AIR_FAN_STATUS_ACTIVE,
    SUPPLY_AIR_FAN_STATUS_DISABLED,
    SUPPLY_AIR_FAN_STATUS_ERROR,
    SUPPLY_AIR_FAN_STATUS_STANDBY,
    SUPPLY_AIR_FAN_STATUS_STARTUP,
)

# Heat pump status mapping
# Status Wärmepumpe: 0=Aus, 5=WP Heizen, 49=WP Kühlen
HEAT_PUMP_STATUSES = {
    HEAT_PUMP_STATUS_OFF: "Off",
    HEAT_PUMP_STATUS_HEATING: "Heating",
    HEAT_PUMP_STATUS_COOLING: "Cooling",
}

# Supply air fan status mapping
# Status Gebläse Zuluft: 0=Deaktiviert, 1=Anlaufphase, 2=Aktiv, 5=Standby, 6=Fehler
SUPPLY_AIR_FAN_STATUSES = {
    SUPPLY_AIR_FAN_STATUS_DISABLED: "Disabled",
    SUPPLY_AIR_FAN_STATUS_STARTUP: "Startup",
    SUPPLY_AIR_FAN_STATUS_ACTIVE: "Active",
    SUPPLY_AIR_FAN_STATUS_STANDBY: "Standby",
    SUPPLY_AIR_FAN_STATUS_ERROR: "Error",
}

# Exhaust air fan status mapping
# Status Gebläse Abluft: 0=Deaktiviert, 1=Anlaufphase, 2=Aktiv, 5=Standby, 6=Fehler
EXHAUST_AIR_FAN_STATUSES = {
    EXHAUST_AIR_FAN_STATUS_DISABLED: "Disabled",
    EXHAUST_AIR_FAN_STATUS_STARTUP: "Startup",
    EXHAUST_AIR_FAN_STATUS_ACTIVE: "Active",
    EXHAUST_AIR_FAN_STATUS_STANDBY: "Standby",
    EXHAUST_AIR_FAN_STATUS_ERROR: "Error",
}

# EWT state mapping
# EWT Zustand: 0=EWT aus/geschlossen, 1=EWT im Heizbetrieb aktiv, 2=EWT im Kühlbetrieb aktiv
EWT_STATES = {
    EWT_STATE_OFF: "Off",
    EWT_STATE_HEATING: "Heating",
    EWT_STATE_COOLING: "Cooling",
}

# Bypass state mapping
# Bypass Zustand: 0=Bypass geschlossen, 1=Bypass offen (Kühlen), 2=Bypass offen (Heizen)
BYPASS_STATES = {
    BYPASS_STATE_CLOSED: "Closed",
    BYPASS_STATE_OPEN_COOLING: "Open (Cooling)",
    BYPASS_STATE_OPEN_HEATING: "Open (Heating)",
}

# Outdoor damper state mapping
# Aussenklappe Zustand: 0=geschlossen, 1=offen
OUTDOOR_DAMPER_STATES = {
    OUTDOOR_DAMPER_STATE_CLOSED: "Closed",
    OUTDOOR_DAMPER_STATE_OPEN: "Open",
}

async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up sensors from a config entry."""
    coordinator: Coordinator = hass.data[DOMAIN][entry.entry_id]
    rooms: list[dict[str, Any]] = entry.data.get(CONF_ROOMS, [])
    has_heating = coordinator.has_heating()

    entities = [
        CurrentFanLevelSensor(coordinator),
        TimeProgramBaseLevelSensor(coordinator),
        ShockVentilationRemainingSensor(coordinator),
        SupplyAirFanStatusSensor(coordinator),
        ExhaustAirFanStatusSensor(coordinator),
        BypassStateSensor(coordinator),
        OutdoorDamperStateSensor(coordinator),
        TimeProgramFanLevelSensor(coordinator),
        SensorFanLevelSensor(coordinator),
        CurrentSupplyAirFlowSensor(coordinator),
        CurrentExhaustAirFlowSensor(coordinator),
        CurrentSupplyAirRpmSensor(coordinator),
        CurrentExhaustAirRpmSensor(coordinator),
        TemperatureT1AfterEwtSensor(coordinator),
        TemperatureT5ExhaustAirSensor(coordinator),
        TemperatureT6InWtSensor(coordinator),
        TemperatureT10OutdoorSensor(coordinator),
        DeviceFilterRemainingSensor(coordinator),
        UpstreamFilterRemainingSensor(coordinator),
        ErrorMessageSensor(coordinator),
    ]
    # Add heating-related sensors only for WGT devices
    if has_heating:
        entities.extend([
            HeatPumpStatusSensor(coordinator),
            EwtStateSensor(coordinator),
            TemperatureT2AfterVhrSensor(coordinator),
            TemperatureT3BeforeNeSensor(coordinator),
            TemperatureT4AfterNeSensor(coordinator),
            TemperatureT7EvaporatorSensor(coordinator),
            TemperatureT8CondenserSensor(coordinator),
        ])

    # Add room-specific sensors
    for room in rooms:
        entities.append(
            (RoomAuxiliaryHeatingSensor if has_heating else RoomTemperatureSensor)(
                    coordinator, room["number"]
            )
        )

    # Add operating hours sensors
    entities.extend([
        OperatingHoursSensor(coordinator, REG_OPERATING_HOURS_FAN),
        OperatingHoursSensor(coordinator, REG_OPERATING_HOURS_FAN_LEVEL_1),
        OperatingHoursSensor(coordinator, REG_OPERATING_HOURS_FAN_LEVEL_2),
        OperatingHoursSensor(coordinator, REG_OPERATING_HOURS_FAN_LEVEL_3),
        OperatingHoursSensor(coordinator, REG_OPERATING_HOURS_FAN_LEVEL_4),
    ])

    # Add heating-related operating hours sensors only for WGT
    if has_heating:
        entities.extend([
            OperatingHoursSensor(coordinator, REG_OPERATING_HOURS_HEAT_PUMP),
            OperatingHoursSensor(coordinator, REG_OPERATING_HOURS_HEAT_PUMP_COOLING,),
            OperatingHoursSensor(coordinator, REG_OPERATING_HOURS_VHR),
            OperatingHoursSensor(coordinator, REG_OPERATING_HOURS_AUXILIARY_HEATING_HOUSE),
            OperatingHoursSensor(coordinator, REG_OPERATING_HOURS_EWT),
        ])

    async_add_entities(entities)

class CurrentFanLevelSensor(AbstractSensor):
    def __init__(self, coordinator: Coordinator) -> None:
        super().__init__(coordinator, REG_CURRENT_FAN_LEVEL)

class TimeProgramBaseLevelSensor(AbstractSensor):
    _attr_state_class = SensorStateClass.MEASUREMENT
    _attr_entity_registry_enabled_default = False

    def __init__(self, coordinator: Coordinator) -> None:
        super().__init__(coordinator, REG_TIME_PROGRAM_BASE_LEVEL)

class ShockVentilationRemainingSensor(AbstractSensor):
    _attr_device_class = SensorDeviceClass.DURATION
    _attr_native_unit_of_measurement = UnitOfTime.MINUTES

    def __init__(self, coordinator: Coordinator) -> None:
        super().__init__(coordinator, REG_SHOCK_VENTILATION_REMAINING)


class HeatPumpStatusSensor(AbstractSensor):
    def __init__(self, coordinator: Coordinator) -> None:
        super().__init__(coordinator, REG_HEAT_PUMP_STATUS)


class SupplyAirFanStatusSensor(AbstractSensor):
    _attr_entity_registry_enabled_default = False

    def __init__(self, coordinator: Coordinator) -> None:
        super().__init__(coordinator, REG_SUPPLY_AIR_FAN_STATUS)


class ExhaustAirFanStatusSensor(AbstractSensor):
    _attr_entity_registry_enabled_default = False

    def __init__(self, coordinator: Coordinator) -> None:
        super().__init__(coordinator, REG_EXHAUST_AIR_FAN_STATUS)


class EwtStateSensor(AbstractSensor):
    _attr_entity_registry_enabled_default = False

    def __init__(self, coordinator: Coordinator) -> None:
        super().__init__(coordinator, REG_EWT_STATE)


class BypassStateSensor(AbstractSensor):
    def __init__(self, coordinator: Coordinator) -> None:
        super().__init__(coordinator, REG_BYPASS_STATE)


class OutdoorDamperStateSensor(AbstractSensor):
    def __init__(self, coordinator: Coordinator) -> None:
        super().__init__(coordinator, REG_OUTDOOR_DAMPER_STATE)


class TimeProgramFanLevelSensor(AbstractSensor):
    _attr_entity_registry_enabled_default = False

    def __init__(self, coordinator: Coordinator) -> None:
        super().__init__(coordinator, REG_TIME_PROGRAM_FAN_LEVEL)


class SensorFanLevelSensor(AbstractSensor):
    _attr_entity_registry_enabled_default = False

    def __init__(self, coordinator: Coordinator) -> None:
        super().__init__(coordinator, REG_SENSOR_FAN_LEVEL)


class CurrentSupplyAirFlowSensor(AbstractSensor):
    _attr_entity_registry_enabled_default = False

    def __init__(self, coordinator: Coordinator) -> None:
        super().__init__(coordinator, REG_CURRENT_SUPPLY_AIR_FLOW)


class CurrentExhaustAirFlowSensor(AbstractSensor):
    _attr_entity_registry_enabled_default = False

    def __init__(self, coordinator: Coordinator) -> None:
        super().__init__(coordinator, REG_CURRENT_EXHAUST_AIR_FLOW)


class CurrentSupplyAirRpmSensor(AbstractSensor):
    _attr_entity_registry_enabled_default = False

    def __init__(self, coordinator: Coordinator) -> None:
        super().__init__(coordinator, REG_CURRENT_SUPPLY_AIR_RPM)


class CurrentExhaustAirRpmSensor(AbstractSensor):
    _attr_entity_registry_enabled_default = False

    def __init__(self, coordinator: Coordinator) -> None:
        super().__init__(coordinator, REG_CURRENT_EXHAUST_AIR_RPM)


class TemperatureT1AfterEwtSensor(AbstractSensor):
    _attr_device_class = SensorDeviceClass.TEMPERATURE
    _attr_native_unit_of_measurement = UnitOfTemperature.CELSIUS
    _attr_entity_registry_enabled_default = False

    def __init__(self, coordinator: Coordinator) -> None:
        super().__init__(coordinator, REG_TEMP_T1_AFTER_EWT)


class TemperatureT2AfterVhrSensor(AbstractSensor):
    _attr_device_class = SensorDeviceClass.TEMPERATURE
    _attr_native_unit_of_measurement = UnitOfTemperature.CELSIUS

    def __init__(self, coordinator: Coordinator) -> None:
        super().__init__(coordinator, REG_TEMP_T2_AFTER_VHR)


class TemperatureT3BeforeNeSensor(AbstractSensor):
    _attr_device_class = SensorDeviceClass.TEMPERATURE
    _attr_native_unit_of_measurement = UnitOfTemperature.CELSIUS

    def __init__(self, coordinator: Coordinator) -> None:
        super().__init__(coordinator, REG_TEMP_T3_BEFORE_NE)


class TemperatureT4AfterNeSensor(AbstractSensor):
    _attr_device_class = SensorDeviceClass.TEMPERATURE
    _attr_native_unit_of_measurement = UnitOfTemperature.CELSIUS

    def __init__(self, coordinator: Coordinator) -> None:
        super().__init__(coordinator, REG_TEMP_T4_AFTER_NE)


class TemperatureT5ExhaustAirSensor(AbstractSensor):
    _attr_device_class = SensorDeviceClass.TEMPERATURE
    _attr_native_unit_of_measurement = UnitOfTemperature.CELSIUS

    def __init__(self, coordinator: Coordinator) -> None:
        super().__init__(coordinator, REG_TEMP_T5_EXHAUST_AIR)


class TemperatureT6InWtSensor(AbstractSensor):
    _attr_device_class = SensorDeviceClass.TEMPERATURE
    _attr_native_unit_of_measurement = UnitOfTemperature.CELSIUS

    def __init__(self, coordinator: Coordinator) -> None:
        super().__init__(coordinator, REG_TEMP_T6_IN_WT)


class TemperatureT7EvaporatorSensor(AbstractSensor):
    _attr_device_class = SensorDeviceClass.TEMPERATURE
    _attr_native_unit_of_measurement = UnitOfTemperature.CELSIUS

    def __init__(self, coordinator: Coordinator) -> None:
        super().__init__(coordinator, REG_TEMP_T7_EVAPORATOR)


class TemperatureT8CondenserSensor(AbstractSensor):
    _attr_device_class = SensorDeviceClass.TEMPERATURE
    _attr_native_unit_of_measurement = UnitOfTemperature.CELSIUS

    def __init__(self, coordinator: Coordinator) -> None:
        super().__init__(coordinator, REG_TEMP_T8_CONDENSER)


class TemperatureT10OutdoorSensor(AbstractSensor):
    _attr_device_class = SensorDeviceClass.TEMPERATURE
    _attr_native_unit_of_measurement = UnitOfTemperature.CELSIUS

    def __init__(self, coordinator: Coordinator) -> None:
        super().__init__(coordinator, REG_TEMP_T10_OUTDOOR)


class DeviceFilterRemainingSensor(AbstractSensor):
    _attr_device_class = SensorDeviceClass.DURATION
    _attr_native_unit_of_measurement = UnitOfTime.DAYS

    def __init__(self, coordinator: Coordinator) -> None:
        super().__init__(coordinator, REG_DEVICE_FILTER_REMAINING)


class UpstreamFilterRemainingSensor(AbstractSensor):
    _attr_device_class = SensorDeviceClass.DURATION
    _attr_native_unit_of_measurement = UnitOfTime.DAYS
    _attr_entity_registry_enabled_default = False

    def __init__(self, coordinator: Coordinator) -> None:
        super().__init__(coordinator, REG_UPSTREAM_FILTER_REMAINING)


class ErrorMessageSensor(AbstractSensor):
    def __init__(self, coordinator: Coordinator) -> None:
        super().__init__(coordinator, REG_ERROR_MESSAGE)

class OperatingHoursSensor(AbstractSensor):
    _attr_device_class = SensorDeviceClass.DURATION
    _attr_state_class = SensorStateClass.TOTAL_INCREASING
    _attr_native_unit_of_measurement = UnitOfTime.HOURS
    _attr_entity_registry_enabled_default = False

    def __init__(self, coordinator: Coordinator, register: int) -> None:
        super().__init__(coordinator, register)


## Room Sensors

# TODO should be a binary sensor
class RoomAuxiliaryHeatingSensor(AbstarctRoomSensor):
    _attr_entity_registry_enabled_default = False

    def __init__(self, coordinator: Coordinator, room_number: int) -> None:
        super().__init__(coordinator, room_number, REG_AUXILIARY_HEATING_ENABLED_ROOM_1)

    @property
    def native_value(self) -> str | None:
        # TODO find a better solution for the value mapping
        value = super().native_value
        if value == 0:
            return "Blocked"
        elif value == 1:
            return "Heating Enabled"
        return None

class RoomTemperatureSensor(AbstarctRoomSensor):
    _attr_device_class = SensorDeviceClass.TEMPERATURE
    _attr_state_class = SensorStateClass.MEASUREMENT
    _attr_native_unit_of_measurement = UnitOfTemperature.CELSIUS

    def __init__(self, coordinator: Coordinator, room_number: int) -> None:
        super().__init__(coordinator, room_number,  REG_CURRENT_TEMPERATURE_1)

