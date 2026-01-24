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
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .abstract import AbstarctRoomSensor, AbstractSensor
from .const import CONF_ROOMS, DOMAIN
from .coordinator import Coordinator
from .modbus.registers import (
    REG_AUXILIARY_HEATING_ENABLED_ROOM_1,
    REG_BYPASS_STATE,
    REG_CURRENT_EXHAUST_AIR_FLOW,
    REG_CURRENT_EXHAUST_AIR_RPM,
    REG_CURRENT_FAN_LEVEL,
    REG_CURRENT_SUPPLY_AIR_FLOW,
    REG_CURRENT_SUPPLY_AIR_RPM,
    REG_CURRENT_TEMPERATURE_1,
    REG_DEVICE_FILTER_REMAINING,
    REG_ERROR_MESSAGE,
    REG_GROUND_HEAT_EXCHANGER_STATE,
    REG_EXHAUST_AIR_FAN_STATUS,
    REG_HEAT_PUMP_STATUS,
    REG_OPERATING_HOURS_AUXILIARY_HEATING_HOUSE,
    REG_OPERATING_HOURS_GROUND_HEAT_EXCHANGER,
    REG_OPERATING_HOURS_FAN,
    REG_OPERATING_HOURS_FAN_LEVEL_1,
    REG_OPERATING_HOURS_FAN_LEVEL_2,
    REG_OPERATING_HOURS_FAN_LEVEL_3,
    REG_OPERATING_HOURS_FAN_LEVEL_4,
    REG_OPERATING_HOURS_HEAT_PUMP,
    REG_OPERATING_HOURS_HEAT_PUMP_COOLING,
    REG_OPERATING_HOURS_PREHEATING_COIL,
    REG_OUTDOOR_DAMPER_STATE,
    REG_SENSOR_FAN_LEVEL,
    REG_SHOCK_VENTILATION_REMAINING,
    REG_SUPPLY_AIR_FAN_STATUS,
    REG_TEMP_T1_AFTER_GROUND_HEAT_EXCHANGER,
    REG_TEMP_T2_AFTER_PREHEATING_COIL,
    REG_TEMP_T3_BEFORE_REHEATER,
    REG_TEMP_T4_AFTER_REHEATER,
    REG_TEMP_T5_EXHAUST_AIR,
    REG_TEMP_T6_IN_HEAT_EXCHANGER,
    REG_TEMP_T7_EVAPORATOR,
    REG_TEMP_T8_CONDENSER,
    REG_TEMP_T10_OUTDOOR,
    REG_TIME_PROGRAM_BASE_LEVEL,
    REG_TIME_PROGRAM_FAN_LEVEL,
    REG_UPSTREAM_FILTER_REMAINING,
)

_LOGGER = logging.getLogger(__name__)

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
        TimeProgramFanLevelSensor(coordinator),
        SensorFanLevelSensor(coordinator),
        CurrentSupplyAirFlowSensor(coordinator),
        CurrentExhaustAirFlowSensor(coordinator),
        CurrentSupplyAirRpmSensor(coordinator),
        CurrentExhaustAirRpmSensor(coordinator),
        TemperatureT1AfterGroundHeatExchangerSensor(coordinator),
        TemperatureT5ExhaustAirSensor(coordinator),
        TemperatureT6InHeatExchangerSensor(coordinator),
        TemperatureT10OutdoorSensor(coordinator),
        DeviceFilterRemainingSensor(coordinator),
        UpstreamFilterRemainingSensor(coordinator),
        ErrorMessageSensor(coordinator),
        # Add operating hours sensors
        OperatingHoursSensor(coordinator, REG_OPERATING_HOURS_FAN),
        OperatingHoursSensor(coordinator, REG_OPERATING_HOURS_FAN_LEVEL_1),
        OperatingHoursSensor(coordinator, REG_OPERATING_HOURS_FAN_LEVEL_2),
        OperatingHoursSensor(coordinator, REG_OPERATING_HOURS_FAN_LEVEL_3),
        OperatingHoursSensor(coordinator, REG_OPERATING_HOURS_FAN_LEVEL_4),
    ]
    # Add heating-related sensors only for WGT devices
    if has_heating:
        entities.extend([
            HeatPumpStatusSensor(coordinator),
            GroundHeatExchangerStateSensor(coordinator),
            TemperatureT2AfterPreheatingCoilSensor(coordinator),
            TemperatureT3BeforeReheaterSensor(coordinator),
            TemperatureT4AfterReheaterSensor(coordinator),
            TemperatureT7EvaporatorSensor(coordinator),
            TemperatureT8CondenserSensor(coordinator),
            # Add heating-related operating hours sensors only for WGT
            OperatingHoursSensor(coordinator, REG_OPERATING_HOURS_HEAT_PUMP),
            OperatingHoursSensor(coordinator, REG_OPERATING_HOURS_HEAT_PUMP_COOLING,),
            OperatingHoursSensor(coordinator, REG_OPERATING_HOURS_PREHEATING_COIL),
            OperatingHoursSensor(coordinator, REG_OPERATING_HOURS_AUXILIARY_HEATING_HOUSE),
            OperatingHoursSensor(coordinator, REG_OPERATING_HOURS_GROUND_HEAT_EXCHANGER),
        ])
    
    # Add room temperature sensors for WRT devices only
    if not has_heating:
        for room in rooms:
            entities.append(RoomTemperatureSensor(coordinator, room["number"]))

    async_add_entities(entities)


class CurrentFanLevelSensor(AbstractSensor):
    """
    Sensor for current fan level
    (Aktuelle Luftstufe)

    Register: 102
    Values:     0 = Off
                1 = Level 1
                2 = Level 2
                3 = Level 3
                4 = Level 4
    """
    def __init__(self, coordinator: Coordinator) -> None:
        super().__init__(coordinator, REG_CURRENT_FAN_LEVEL)

class TimeProgramBaseLevelSensor(AbstractSensor):
    """
    Sensor for time program base level
    (Zeitprogramm Basis Luftstufe)

    Register: 110
    Values:     0 = Off
                1 = Level 1
                2 = Level 2
                3 = Level 3
                4 = Level 4
    """
    def __init__(self, coordinator: Coordinator) -> None:
        super().__init__(
            coordinator,
            REG_TIME_PROGRAM_BASE_LEVEL,
            enabled_by_default = False
        )

class ShockVentilationRemainingSensor(AbstractSensor):
    """
    Sensor for shock ventilation remaining time
    (Stoßlüftung verbleibende Zeit)

    Register: 112
    Values:   0-60 (minutes)
    """
    def __init__(self, coordinator: Coordinator) -> None:
        super().__init__(
            coordinator,
            REG_SHOCK_VENTILATION_REMAINING,
            device_class = SensorDeviceClass.DURATION,
            unit_of_measurement = UnitOfTime.MINUTES,
        )

class HeatPumpStatusSensor(AbstractSensor):
    """
    Sensor for heat pump status
    (Status Wärmepumpe)

    Register: 114
    Values:     0 = Off
                5 = Heating
               49 = Cooling
    """
    def __init__(self, coordinator: Coordinator) -> None:
        super().__init__(coordinator, REG_HEAT_PUMP_STATUS)

class SupplyAirFanStatusSensor(AbstractSensor):
    """Sensor for supply air fan status
    (Status Gebläse Zuluft)

    Register: 117
    Values:     0 = Deactivated
                1 = Startup Phase
                2 = Active
                3 = Standby
                4 = Error
    """
    def __init__(self, coordinator: Coordinator) -> None:
        super().__init__(coordinator, REG_SUPPLY_AIR_FAN_STATUS, enabled_by_default=False)

class ExhaustAirFanStatusSensor(AbstractSensor):
    """
    Sensor for exhaust air fan status"
    (Status Gebläse Abluft)

    Register: 118
    Values:     0 = Deactivated
                1 = Startup Phase
                2 = Active
                3 = Standby
                4 = Error
    """
    def __init__(self, coordinator: Coordinator) -> None:
        super().__init__(coordinator, REG_EXHAUST_AIR_FAN_STATUS, enabled_by_default=False)

class GroundHeatExchangerStateSensor(AbstractSensor):
    """
    Sensor for ground heat exchanger state
    (Status Erdwärmetauscher/EWT ZUstand)

    Register: 121
    Values:     0 = Off/closed
                1 = Ground heat exchanger active in heating mode
                2 = Ground heat exchanger active in cooling mode
    """
    def __init__(self, coordinator: Coordinator) -> None:
        super().__init__(coordinator, REG_GROUND_HEAT_EXCHANGER_STATE, enabled_by_default=False)

class BypassStateSensor(AbstractSensor):
    """
    Sensor for bypass state
    (Bypass ZUstand)

    Register: 123
    Values:     0 = Closed
                1 = Open (cooling mode)
                2 = Open (heating mode)
    """
    def __init__(self, coordinator: Coordinator) -> None:
        super().__init__(coordinator, REG_BYPASS_STATE, enabled_by_default=False)

class TimeProgramFanLevelSensor(AbstractSensor):
    """
    Sensor for time program fan level
    (Zeitprogramm Luftstufe)

    Register: 140
    Values:     0 = Off
                1 = Level 1
                2 = Level 2
                3 = Level 3
                4 = Level 4
    """
    def __init__(self, coordinator: Coordinator) -> None:
        super().__init__(coordinator, REG_TIME_PROGRAM_FAN_LEVEL, enabled_by_default=False)

class SensorFanLevelSensor(AbstractSensor):
    """
    Sensor for sensor fan level
    (Luftstufe Sensoren)

    Register: 140
    Values:     0 = Off
                1 = Level 1
                2 = Level 2
                3 = Level 3
                4 = Level 4
    """
    def __init__(self, coordinator: Coordinator) -> None:
        super().__init__(coordinator, REG_SENSOR_FAN_LEVEL, enabled_by_default=False)

class CurrentSupplyAirFlowSensor(AbstractSensor):
    """
    Sensor for current supply air flow
    (Luftleistung aktuell Zuluft)

    Register: 142
    Values:   0-100 (%)
    """
    def __init__(self, coordinator: Coordinator) -> None:
        super().__init__(
            coordinator,
            REG_CURRENT_SUPPLY_AIR_FLOW,
            unit_of_measurement="%",
            state_class=SensorStateClass.MEASUREMENT,
            enabled_by_default=False,
        )

class CurrentExhaustAirFlowSensor(AbstractSensor):
    """
    Sensor for current exhaust air flow
    (Luftleistung aktuell Abluft)

    Register: 143
    Values:   0-100 (%)
    """
    def __init__(self, coordinator: Coordinator) -> None:
        super().__init__(
            coordinator,
            REG_CURRENT_EXHAUST_AIR_FLOW,
            unit_of_measurement="%",
            state_class=SensorStateClass.MEASUREMENT,
            enabled_by_default=False
        )

class CurrentSupplyAirRpmSensor(AbstractSensor):
    """
    Sensor for current supply air RPM
    (Aktuelle Drehzahl Zuluft)

    Register: 144
    Values:   0-10000 (RPM)
    """
    def __init__(self, coordinator: Coordinator) -> None:
        super().__init__(
            coordinator,
            REG_CURRENT_SUPPLY_AIR_RPM,
            unit_of_measurement="rpm",
            state_class=SensorStateClass.MEASUREMENT,
            enabled_by_default=False
        )

class CurrentExhaustAirRpmSensor(AbstractSensor):
    """
    Sensor for current exhaust air RPM
    (Aktuelle Drehzahl Abluft)

    Register: 144
    Values:   0-10000 (RPM)
    """
    def __init__(self, coordinator: Coordinator) -> None:
        super().__init__(
            coordinator,
            REG_CURRENT_EXHAUST_AIR_RPM,
            unit_of_measurement="rpm",
            state_class=SensorStateClass.MEASUREMENT,
            enabled_by_default=False
        )

class TemperatureT1AfterGroundHeatExchangerSensor(AbstractSensor):
    """
    Sensor for temperature T1 after ground heat exchanger
    (Temperatur T1 nach Erdwärmetauscher/EWT)

    Register: 200
    Values:   -50-100 (°C)
    """
    def __init__(self, coordinator: Coordinator) -> None:
        super().__init__(
            coordinator,
            REG_TEMP_T1_AFTER_GROUND_HEAT_EXCHANGER,
            device_class=SensorDeviceClass.TEMPERATURE,
            unit_of_measurement=UnitOfTemperature.CELSIUS,
            enabled_by_default=False,
        )

class TemperatureT2AfterPreheatingCoilSensor(AbstractSensor):
    """
    Sensor for temperature T2 after preheating coil
    (Temperatur T2 nach Vorheizregister/VHR)

    Register: 201
    Values:   -50-100 (°C)
    """
    def __init__(self, coordinator: Coordinator) -> None:
        super().__init__(
            coordinator,
            REG_TEMP_T2_AFTER_PREHEATING_COIL,
            device_class=SensorDeviceClass.TEMPERATURE,
            unit_of_measurement=UnitOfTemperature.CELSIUS,
            enabled_by_default=False,
        )

class TemperatureT3BeforeReheaterSensor(AbstractSensor):
    """
    Sensor for temperature T3 before Reheater
    (Temperatur T3 vor Nacherwärmung/NE)

    Register: 202
    Values:   -50-100 (°C)
    """
    def __init__(self, coordinator: Coordinator) -> None:
        super().__init__(
            coordinator,
            REG_TEMP_T3_BEFORE_REHEATER,
            device_class=SensorDeviceClass.TEMPERATURE,
            unit_of_measurement=UnitOfTemperature.CELSIUS,
            enabled_by_default=False,
        )

class TemperatureT4AfterReheaterSensor(AbstractSensor):
    """
    Sensor for temperature T3 after Reheater
    (Temperatur T3 nach Nacherwärmung/NE)

    Register: 203
    Values:   -50-100 (°C)
    """
    def __init__(self, coordinator: Coordinator) -> None:
        super().__init__(
            coordinator,
            REG_TEMP_T4_AFTER_REHEATER,
            device_class=SensorDeviceClass.TEMPERATURE,
            unit_of_measurement=UnitOfTemperature.CELSIUS,
            enabled_by_default=False,
        )

class TemperatureT5ExhaustAirSensor(AbstractSensor):
    """
    Senso
    (Temperatur T5 Abluft)

    Register: 204
    Values:   -50-100 (°C)
    """
    def __init__(self, coordinator: Coordinator) -> None:
        super().__init__(
            coordinator,
            REG_TEMP_T5_EXHAUST_AIR,
            device_class=SensorDeviceClass.TEMPERATURE,
            unit_of_measurement=UnitOfTemperature.CELSIUS,
            enabled_by_default=False,
        )


class TemperatureT6InHeatExchangerSensor(AbstractSensor):
    """
    Sensor for temperature T6 in heat exchanger
    (Temperatur T6 im Wärmetauscher/WT)

    Register: 205
    Values:   -50-100 (°C)
    """
    def __init__(self, coordinator: Coordinator) -> None:
        super().__init__(
            coordinator,
            REG_TEMP_T6_IN_HEAT_EXCHANGER,
            device_class=SensorDeviceClass.TEMPERATURE,
            unit_of_measurement=UnitOfTemperature.CELSIUS,
            enabled_by_default=False,
        )

class TemperatureT7EvaporatorSensor(AbstractSensor):
    """
    Sensor for temperature T7 evaporator
    (Temperatur T7 Verdampfer)

    Register: 206
    Values:   -50-100 (°C)
    """
    def __init__(self, coordinator: Coordinator) -> None:
        super().__init__(
            coordinator,
            REG_TEMP_T7_EVAPORATOR,
            device_class=SensorDeviceClass.TEMPERATURE,
            unit_of_measurement=UnitOfTemperature.CELSIUS,
            enabled_by_default=False,
        )

class TemperatureT8CondenserSensor(AbstractSensor):
    """
    Sensor for temperature T8 condenser
    (Temperatur T7 Kondensator)

    Register: 207
    Values:   -50-100 (°C)
    """
    def __init__(self, coordinator: Coordinator) -> None:
        super().__init__(
            coordinator,
            REG_TEMP_T8_CONDENSER,
            device_class=SensorDeviceClass.TEMPERATURE,
            unit_of_measurement=UnitOfTemperature.CELSIUS,
            enabled_by_default=False,
        )

class TemperatureT10OutdoorSensor(AbstractSensor):
    """
    Sensor for temperature T10 outdoor
    (Temperatur T10 Außen)

    Register: 209
    Values:   -50-100 (°C)
    """
    def __init__(self, coordinator: Coordinator) -> None:
        super().__init__(
            coordinator,
            REG_TEMP_T10_OUTDOOR,
            device_class=SensorDeviceClass.TEMPERATURE,
            unit_of_measurement=UnitOfTemperature.CELSIUS,
        )

class DeviceFilterRemainingSensor(AbstractSensor):
    """
    Sensor for device filter remaining time
    (Restlaufzeit Gerätefilter)

    Register: 265
    Values:   0-255 (days)
    """
    def __init__(self, coordinator: Coordinator) -> None:
        super().__init__(
            coordinator,
            REG_DEVICE_FILTER_REMAINING,
            device_class=SensorDeviceClass.DURATION,
            unit_of_measurement=UnitOfTime.DAYS,
        )

class UpstreamFilterRemainingSensor(AbstractSensor):
    """
    Sensor for upstream filter remaining time
    (Restlaufzeit Vorgelagerter Filter)

    Register: 263
    Values:   0-255 (days)
    """
    def __init__(self, coordinator: Coordinator) -> None:
        super().__init__(
            coordinator,
            REG_UPSTREAM_FILTER_REMAINING,
            device_class=SensorDeviceClass.DURATION,
            unit_of_measurement=UnitOfTime.DAYS,
            enabled_by_default=False,
        )

class ErrorMessageSensor(AbstractSensor):
    """
    Sensor for error message
    (Fehlermeldung)

    Register: 240
    Values:     0 = No error
    """
    def __init__(self, coordinator: Coordinator) -> None:
        super().__init__(coordinator, REG_ERROR_MESSAGE)

class OperatingHoursSensor(AbstractSensor):
    def __init__(self, coordinator: Coordinator, register: int) -> None:
        super().__init__(
            coordinator,
            register,
            device_class=SensorDeviceClass.DURATION,
            state_class=SensorStateClass.TOTAL_INCREASING,
            unit_of_measurement=UnitOfTime.HOURS,
            enabled_by_default=False,
        )

## Room Sensors

class RoomTemperatureSensor(AbstarctRoomSensor):
    def __init__(self, coordinator: Coordinator, room_number: int) -> None:
        super().__init__(
            coordinator,
            REG_CURRENT_TEMPERATURE_1,
            room_number,
            device_class = SensorDeviceClass.TEMPERATURE,
            state_class = SensorStateClass.MEASUREMENT,
            unit_of_measurement = UnitOfTemperature.CELSIUS,
        )

