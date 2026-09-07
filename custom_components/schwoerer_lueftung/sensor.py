"""Sensor platform for Schwörer Lüftung."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Any

from homeassistant.components.sensor import (
    SensorDeviceClass,
    SensorEntity,
    SensorEntityDescription,
    SensorStateClass,
)
from homeassistant.const import EntityCategory, UnitOfTemperature, UnitOfTime
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.util import dt as dt_util

from .const import CONF_ROOMS
from .coordinator import SchwoererConfigEntry
from .entity import ROOMS, SchwoererEntity, SchwoererEntityDescription

# Value maps for the coded registers. These are presentation: the device model
# carries the numbers, and the strings here are what the translations key off.
BYPASS_STATE = {0: "closed", 1: "open_cooling", 2: "open_heating"}
EXHAUST_AIR_FAN_STATUS = {
    0: "disabled",
    1: "startup",
    2: "active",
    5: "standby",
    6: "error",
}
GROUND_HEAT_EXCHANGER_STATE = {0: "off", 1: "heating", 2: "cooling"}
HEAT_PUMP_STATUS = {0: "off", 5: "heating", 49: "cooling"}
SUPPLY_AIR_FAN_STATUS = {
    0: "disabled",
    1: "startup",
    2: "active",
    5: "standby",
    6: "error",
}


@dataclass(frozen=True, kw_only=True)
class SchwoererSensorEntityDescription(
    SchwoererEntityDescription, SensorEntityDescription
):
    """Describe a sensor backed by a device field."""

    options_map: dict[int, str] | None = None
    """Maps a coded register to its state string, for an enum sensor."""


def _temperature(
    key: str, subsystem: str, *, enabled: bool = False
) -> SchwoererSensorEntityDescription:
    return SchwoererSensorEntityDescription(
        key=key,
        subsystem=subsystem,
        device_class=SensorDeviceClass.TEMPERATURE,
        state_class=SensorStateClass.MEASUREMENT,
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        entity_registry_enabled_default=enabled,
    )


def _operating_hours(key: str, subsystem: str) -> SchwoererSensorEntityDescription:
    return SchwoererSensorEntityDescription(
        key=key,
        subsystem=subsystem,
        device_class=SensorDeviceClass.DURATION,
        state_class=SensorStateClass.TOTAL_INCREASING,
        native_unit_of_measurement=UnitOfTime.HOURS,
        entity_registry_enabled_default=False,
    )


VENTILATION_SENSORS: tuple[SchwoererSensorEntityDescription, ...] = (
    SchwoererSensorEntityDescription(key="current_fan_level", subsystem="ventilation"),
    SchwoererSensorEntityDescription(
        key="time_program_base_level",
        subsystem="ventilation",
        entity_registry_enabled_default=False,
    ),
    SchwoererSensorEntityDescription(
        key="shock_ventilation_remaining",
        subsystem="ventilation",
        device_class=SensorDeviceClass.DURATION,
        native_unit_of_measurement=UnitOfTime.MINUTES,
    ),
    SchwoererSensorEntityDescription(
        key="supply_air_fan_status",
        subsystem="ventilation",
        device_class=SensorDeviceClass.ENUM,
        options_map=SUPPLY_AIR_FAN_STATUS,
        entity_registry_enabled_default=False,
    ),
    SchwoererSensorEntityDescription(
        key="exhaust_air_fan_status",
        subsystem="ventilation",
        device_class=SensorDeviceClass.ENUM,
        options_map=EXHAUST_AIR_FAN_STATUS,
        entity_registry_enabled_default=False,
    ),
    SchwoererSensorEntityDescription(
        key="bypass_state",
        subsystem="ventilation",
        device_class=SensorDeviceClass.ENUM,
        options_map=BYPASS_STATE,
        entity_registry_enabled_default=False,
    ),
    SchwoererSensorEntityDescription(
        key="time_program_fan_level",
        subsystem="ventilation",
        entity_registry_enabled_default=False,
    ),
    SchwoererSensorEntityDescription(
        key="sensor_fan_level",
        subsystem="ventilation",
        entity_registry_enabled_default=False,
    ),
    SchwoererSensorEntityDescription(
        key="current_supply_air_flow",
        subsystem="ventilation",
        native_unit_of_measurement="%",
        state_class=SensorStateClass.MEASUREMENT,
        entity_registry_enabled_default=False,
    ),
    SchwoererSensorEntityDescription(
        key="current_exhaust_air_flow",
        subsystem="ventilation",
        native_unit_of_measurement="%",
        state_class=SensorStateClass.MEASUREMENT,
        entity_registry_enabled_default=False,
    ),
    SchwoererSensorEntityDescription(
        key="current_supply_air_rpm",
        subsystem="ventilation",
        native_unit_of_measurement="rpm",
        state_class=SensorStateClass.MEASUREMENT,
        entity_registry_enabled_default=False,
    ),
    SchwoererSensorEntityDescription(
        key="current_exhaust_air_rpm",
        subsystem="ventilation",
        native_unit_of_measurement="rpm",
        state_class=SensorStateClass.MEASUREMENT,
        entity_registry_enabled_default=False,
    ),
)

TEMPERATURE_SENSORS: tuple[SchwoererSensorEntityDescription, ...] = (
    _temperature("temperature_t5_exhaust_air", "temperatures"),
    _temperature("temperature_t6_in_heat_exchanger", "temperatures"),
    _temperature("temperature_t10_outdoor", "temperatures", enabled=True),
    # Undocumented, so off by default: it was found on one unit and what it
    # measures is unknown.
    _temperature("temperature_t9", "undocumented_temperatures"),
)

# The unit's own real-time clock. Diagnostic, and off by default.
CLOCK_SENSOR = SchwoererSensorEntityDescription(
    key="device_clock",
    subsystem="clock",
    field="datetime",
    device_class=SensorDeviceClass.TIMESTAMP,
    entity_category=EntityCategory.DIAGNOSTIC,
    entity_registry_enabled_default=False,
)

ALARM_SENSORS: tuple[SchwoererSensorEntityDescription, ...] = (
    SchwoererSensorEntityDescription(key="error_message", subsystem="alarms"),
    SchwoererSensorEntityDescription(
        key="device_filter_remaining",
        subsystem="alarms",
        device_class=SensorDeviceClass.DURATION,
        native_unit_of_measurement=UnitOfTime.DAYS,
    ),
    SchwoererSensorEntityDescription(
        key="upstream_filter_remaining",
        subsystem="alarms",
        device_class=SensorDeviceClass.DURATION,
        native_unit_of_measurement=UnitOfTime.DAYS,
        entity_registry_enabled_default=False,
    ),
)

OPERATING_HOURS_SENSORS: tuple[SchwoererSensorEntityDescription, ...] = (
    _operating_hours("operating_hours_fan", "operating_hours"),
    _operating_hours("operating_hours_fan_level_1", "operating_hours"),
    _operating_hours("operating_hours_fan_level_2", "operating_hours"),
    _operating_hours("operating_hours_fan_level_3", "operating_hours"),
    _operating_hours("operating_hours_fan_level_4", "operating_hours"),
)

HEATING_SENSORS: tuple[SchwoererSensorEntityDescription, ...] = (
    SchwoererSensorEntityDescription(
        key="heat_pump_status",
        subsystem="heating",
        device_class=SensorDeviceClass.ENUM,
        options_map=HEAT_PUMP_STATUS,
    ),
    _temperature("temperature_t2_after_preheating_coil", "heating"),
    _temperature("temperature_t3_before_reheater", "heating"),
    _temperature("temperature_t4_after_reheater", "heating"),
    _temperature("temperature_t7_evaporator", "heating"),
    _temperature("temperature_t8_condenser", "heating"),
    _operating_hours("operating_hours_heat_pump", "heating"),
    _operating_hours("operating_hours_heat_pump_cooling", "heating"),
    _operating_hours("operating_hours_preheating_coil", "heating"),
    _operating_hours("operating_hours_auxiliary_heating_house", "heating"),
)

GROUND_HEAT_EXCHANGER_SENSORS: tuple[SchwoererSensorEntityDescription, ...] = (
    _temperature("temperature_t1_after_ground_heat_exchanger", "ground_heat_exchanger"),
    SchwoererSensorEntityDescription(
        key="ground_heat_exchanger_state",
        subsystem="ground_heat_exchanger",
        device_class=SensorDeviceClass.ENUM,
        options_map=GROUND_HEAT_EXCHANGER_STATE,
        entity_registry_enabled_default=False,
    ),
)

# Room temperature is surfaced as a plain sensor only on a WRT. A WGT gets a
# climate entity for the room instead, which carries the same reading.
ROOM_SENSOR = _temperature("current_temperature", ROOMS, enabled=True)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: SchwoererConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up sensors from a config entry."""
    coordinator = entry.runtime_data
    has_heating = coordinator.has_heating()

    descriptions = [
        *VENTILATION_SENSORS,
        *TEMPERATURE_SENSORS,
        *ALARM_SENSORS,
        *OPERATING_HOURS_SENSORS,
        CLOCK_SENSOR,
    ]

    if coordinator.has_ground_heat_exchanger():
        descriptions.extend(GROUND_HEAT_EXCHANGER_SENSORS)

    if has_heating:
        descriptions.extend(HEATING_SENSORS)

    entities: list[SchwoererSensor] = [
        SchwoererSensor(coordinator, description) for description in descriptions
    ]

    if not has_heating:
        entities.extend(
            SchwoererSensor(coordinator, ROOM_SENSOR, room["number"])
            for room in entry.data.get(CONF_ROOMS, [])
        )

    async_add_entities(entities)


class SchwoererSensor(SchwoererEntity, SensorEntity):
    """A sensor reading one device field."""

    entity_description: SchwoererSensorEntityDescription

    def __init__(
        self,
        coordinator,
        description: SchwoererSensorEntityDescription,
        room_number: int | None = None,
    ) -> None:
        super().__init__(coordinator, description, room_number)

        if description.options_map is not None:
            self._attr_options = list(description.options_map.values())

    @property
    def native_value(self) -> Any:
        value = self._value
        if value is None:
            return None

        if (options := self.entity_description.options_map) is not None:
            return options.get(value)

        if isinstance(value, datetime) and value.tzinfo is None:
            # The unit keeps local time with no zone of its own, so read it as
            # Home Assistant's configured one.
            return value.replace(tzinfo=dt_util.DEFAULT_TIME_ZONE)

        return value

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        attributes = super().extra_state_attributes
        if self._room_number is None:
            attributes["raw_value"] = self._value
        return attributes
