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
    REG_EWT_STATE,
    REG_EXHAUST_AIR_FAN_STATUS,
    REG_HEAT_PUMP_STATUS,
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
            EwtStateSensor(coordinator),
            TemperatureT2AfterVhrSensor(coordinator),
            TemperatureT3BeforeNeSensor(coordinator),
            TemperatureT4AfterNeSensor(coordinator),
            TemperatureT7EvaporatorSensor(coordinator),
            TemperatureT8CondenserSensor(coordinator),
            # Add heating-related operating hours sensors only for WGT
            OperatingHoursSensor(coordinator, REG_OPERATING_HOURS_HEAT_PUMP),
            OperatingHoursSensor(coordinator, REG_OPERATING_HOURS_HEAT_PUMP_COOLING,),
            OperatingHoursSensor(coordinator, REG_OPERATING_HOURS_VHR),
            OperatingHoursSensor(coordinator, REG_OPERATING_HOURS_AUXILIARY_HEATING_HOUSE),
            OperatingHoursSensor(coordinator, REG_OPERATING_HOURS_EWT),
        ])
        for room in rooms:
            _LOGGER.debug("::::Adding auxiliary heating sensor for room %d", room["number"])
            entities.append(RoomAuxiliaryHeatingSensor(coordinator, room["number"]))
    else:
        for room in rooms:
            entities.append(RoomTemperatureSensor(coordinator, room["number"]))

    async_add_entities(entities)

class CurrentFanLevelSensor(AbstractSensor):
    def __init__(self, coordinator: Coordinator) -> None:
        super().__init__(coordinator, REG_CURRENT_FAN_LEVEL)

class TimeProgramBaseLevelSensor(AbstractSensor):
    def __init__(self, coordinator: Coordinator) -> None:
        super().__init__(
            coordinator,
            REG_TIME_PROGRAM_BASE_LEVEL,
            state_class = SensorStateClass.MEASUREMENT,
            enabled_by_default = False
        )

class ShockVentilationRemainingSensor(AbstractSensor):
    def __init__(self, coordinator: Coordinator) -> None:
        super().__init__(
            coordinator,
            REG_SHOCK_VENTILATION_REMAINING,
            device_class = SensorDeviceClass.DURATION,
            unit_of_measurement = UnitOfTime.MINUTES,
        )


class HeatPumpStatusSensor(AbstractSensor):
    def __init__(self, coordinator: Coordinator) -> None:
        super().__init__(coordinator, REG_HEAT_PUMP_STATUS)

class SupplyAirFanStatusSensor(AbstractSensor):
    def __init__(self, coordinator: Coordinator) -> None:
        super().__init__(coordinator, REG_SUPPLY_AIR_FAN_STATUS, enabled_by_default=False)

class ExhaustAirFanStatusSensor(AbstractSensor):
    def __init__(self, coordinator: Coordinator) -> None:
        super().__init__(coordinator, REG_EXHAUST_AIR_FAN_STATUS, enabled_by_default=False)

class EwtStateSensor(AbstractSensor):
    def __init__(self, coordinator: Coordinator) -> None:
        super().__init__(coordinator, REG_EWT_STATE, enabled_by_default=False)

class BypassStateSensor(AbstractSensor):
    def __init__(self, coordinator: Coordinator) -> None:
        super().__init__(coordinator, REG_BYPASS_STATE, enabled_by_default=False)

class OutdoorDamperStateSensor(AbstractSensor):
    def __init__(self, coordinator: Coordinator) -> None:
        super().__init__(coordinator, REG_OUTDOOR_DAMPER_STATE)

class TimeProgramFanLevelSensor(AbstractSensor):
    def __init__(self, coordinator: Coordinator) -> None:
        super().__init__(coordinator, REG_TIME_PROGRAM_FAN_LEVEL, enabled_by_default=False)

class SensorFanLevelSensor(AbstractSensor):
    def __init__(self, coordinator: Coordinator) -> None:
        super().__init__(coordinator, REG_SENSOR_FAN_LEVEL, enabled_by_default=False)

class CurrentSupplyAirFlowSensor(AbstractSensor):
    def __init__(self, coordinator: Coordinator) -> None:
        super().__init__(coordinator, REG_CURRENT_SUPPLY_AIR_FLOW, enabled_by_default=False)

class CurrentExhaustAirFlowSensor(AbstractSensor):
    def __init__(self, coordinator: Coordinator) -> None:
        super().__init__(coordinator, REG_CURRENT_EXHAUST_AIR_FLOW, enabled_by_default=False)

class CurrentSupplyAirRpmSensor(AbstractSensor):
    def __init__(self, coordinator: Coordinator) -> None:
        super().__init__(coordinator, REG_CURRENT_SUPPLY_AIR_RPM, enabled_by_default=False)

class CurrentExhaustAirRpmSensor(AbstractSensor):
    def __init__(self, coordinator: Coordinator) -> None:
        super().__init__(coordinator, REG_CURRENT_EXHAUST_AIR_RPM, enabled_by_default=False)

class TemperatureT1AfterEwtSensor(AbstractSensor):
    def __init__(self, coordinator: Coordinator) -> None:
        super().__init__(
            coordinator,
            REG_TEMP_T1_AFTER_EWT,
            device_class=SensorDeviceClass.TEMPERATURE,
            unit_of_measurement=UnitOfTemperature.CELSIUS,
            enabled_by_default=False,
        )

class TemperatureT2AfterVhrSensor(AbstractSensor):
    def __init__(self, coordinator: Coordinator) -> None:
        super().__init__(
            coordinator,
            REG_TEMP_T2_AFTER_VHR,
            device_class=SensorDeviceClass.TEMPERATURE,
            unit_of_measurement=UnitOfTemperature.CELSIUS,
            enabled_by_default=False,
        )

class TemperatureT3BeforeNeSensor(AbstractSensor):
    def __init__(self, coordinator: Coordinator) -> None:
        super().__init__(
            coordinator,
            REG_TEMP_T3_BEFORE_NE,
            device_class=SensorDeviceClass.TEMPERATURE,
            unit_of_measurement=UnitOfTemperature.CELSIUS,
            enabled_by_default=False,
        )

class TemperatureT4AfterNeSensor(AbstractSensor):
    def __init__(self, coordinator: Coordinator) -> None:
        super().__init__(
            coordinator,
            REG_TEMP_T4_AFTER_NE,
            device_class=SensorDeviceClass.TEMPERATURE,
            unit_of_measurement=UnitOfTemperature.CELSIUS,
            enabled_by_default=False,
        )

class TemperatureT5ExhaustAirSensor(AbstractSensor):
    def __init__(self, coordinator: Coordinator) -> None:
        super().__init__(
            coordinator,
            REG_TEMP_T5_EXHAUST_AIR,
            device_class=SensorDeviceClass.TEMPERATURE,
            unit_of_measurement=UnitOfTemperature.CELSIUS,
            enabled_by_default=False,
        )


class TemperatureT6InWtSensor(AbstractSensor):
    def __init__(self, coordinator: Coordinator) -> None:
        super().__init__(
            coordinator,
            REG_TEMP_T6_IN_WT,
            device_class=SensorDeviceClass.TEMPERATURE,
            unit_of_measurement=UnitOfTemperature.CELSIUS,
            enabled_by_default=False,
        )

class TemperatureT7EvaporatorSensor(AbstractSensor):
    def __init__(self, coordinator: Coordinator) -> None:
        super().__init__(
            coordinator,
            REG_TEMP_T7_EVAPORATOR,
            device_class=SensorDeviceClass.TEMPERATURE,
            unit_of_measurement=UnitOfTemperature.CELSIUS,
            enabled_by_default=False,
        )

class TemperatureT8CondenserSensor(AbstractSensor):
    def __init__(self, coordinator: Coordinator) -> None:
        super().__init__(
            coordinator,
            REG_TEMP_T8_CONDENSER,
            device_class=SensorDeviceClass.TEMPERATURE,
            unit_of_measurement=UnitOfTemperature.CELSIUS,
            enabled_by_default=False,
        )

class TemperatureT10OutdoorSensor(AbstractSensor):
    def __init__(self, coordinator: Coordinator) -> None:
        super().__init__(
            coordinator,
            REG_TEMP_T10_OUTDOOR,
            device_class=SensorDeviceClass.TEMPERATURE,
            unit_of_measurement=UnitOfTemperature.CELSIUS,
        )

class DeviceFilterRemainingSensor(AbstractSensor):
    def __init__(self, coordinator: Coordinator) -> None:
        super().__init__(
            coordinator,
            REG_DEVICE_FILTER_REMAINING,
            device_class=SensorDeviceClass.DURATION,
            unit_of_measurement=UnitOfTime.DAYS,
        )

class UpstreamFilterRemainingSensor(AbstractSensor):
    def __init__(self, coordinator: Coordinator) -> None:
        super().__init__(
            coordinator,
            REG_UPSTREAM_FILTER_REMAINING,
            device_class=SensorDeviceClass.DURATION,
            unit_of_measurement=UnitOfTime.DAYS,
            enabled_by_default=False,
        )

class ErrorMessageSensor(AbstractSensor):
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

# TODO should be a binary sensor
class RoomAuxiliaryHeatingSensor(AbstarctRoomSensor):
    def __init__(self, coordinator: Coordinator, room_number: int) -> None:
        super().__init__(
            coordinator,
            REG_AUXILIARY_HEATING_ENABLED_ROOM_1,
            room_number,
            enabled_by_default=True
        )

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
    def __init__(self, coordinator: Coordinator, room_number: int) -> None:
        super().__init__(
            coordinator,
            REG_CURRENT_TEMPERATURE_1,
            room_number,
            device_class = SensorDeviceClass.TEMPERATURE,
            state_class = SensorStateClass.MEASUREMENT,
            unit_of_measurement = UnitOfTemperature.CELSIUS,
        )

