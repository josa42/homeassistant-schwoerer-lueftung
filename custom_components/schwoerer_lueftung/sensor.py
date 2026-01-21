"""Sensor platform"""

from __future__ import annotations

from typing import Any

from homeassistant.components.sensor import (
    SensorDeviceClass,
    SensorEntity,
    SensorStateClass,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import UnitOfTemperature, UnitOfTime
from homeassistant.core import HomeAssistant
from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import CONF_ROOMS, DOMAIN, MANUFACTURER, MODEL_WGT, MODEL_WRT
from .coordinator import Coordinator
from .modbus_client import (
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
        CurrentFanLevelSensor(coordinator, entry),
        TimeProgramBaseLevelSensor(coordinator, entry),
        ShockVentilationRemainingSensor(coordinator, entry),
        SupplyAirFanStatusSensor(coordinator, entry),
        ExhaustAirFanStatusSensor(coordinator, entry),
        BypassStateSensor(coordinator, entry),
        OutdoorDamperStateSensor(coordinator, entry),
        TimeProgramFanLevelSensor(coordinator, entry),
        SensorFanLevelSensor(coordinator, entry),
        CurrentSupplyAirFlowSensor(coordinator, entry),
        CurrentExhaustAirFlowSensor(coordinator, entry),
        CurrentSupplyAirRpmSensor(coordinator, entry),
        CurrentExhaustAirRpmSensor(coordinator, entry),
        TemperatureT1AfterEwtSensor(coordinator, entry),
        TemperatureT5ExhaustAirSensor(coordinator, entry),
        TemperatureT6InWtSensor(coordinator, entry),
        TemperatureT10OutdoorSensor(coordinator, entry),
        DeviceFilterRemainingSensor(coordinator, entry),
        UpstreamFilterRemainingSensor(coordinator, entry),
        ErrorMessageSensor(coordinator, entry),
    ]

    # Add heating-related sensors only for WGT devices
    if has_heating:
        entities.extend([
            HeatPumpStatusSensor(coordinator, entry),
            EwtStateSensor(coordinator, entry),
            TemperatureT2AfterVhrSensor(coordinator, entry),
            TemperatureT3BeforeNeSensor(coordinator, entry),
            TemperatureT4AfterNeSensor(coordinator, entry),
            TemperatureT7EvaporatorSensor(coordinator, entry),
            TemperatureT8CondenserSensor(coordinator, entry),
        ])

    # Add room-specific sensors
    for room in rooms:
        # Add room temperature sensor for WRT devices
        if not has_heating:
            entities.append(
                RoomTemperatureSensor(coordinator, room["number"], room["name"])
            )
        # Add auxiliary heating sensor for WGT devices
        else:
            entities.append(
                RoomAuxiliaryHeatingSensor(coordinator, room["number"], room["name"])
            )

    # Add operating hours sensors
    entities.extend([
        OperatingHoursSensor( coordinator, entry, "operating_hours_fan"),
        OperatingHoursSensor( coordinator, entry, "operating_hours_fan_level_1"),
        OperatingHoursSensor( coordinator, entry, "operating_hours_fan_level_2"),
        OperatingHoursSensor( coordinator, entry, "operating_hours_fan_level_3"),
        OperatingHoursSensor( coordinator, entry, "operating_hours_fan_level_4"),
    ])

    # Add heating-related operating hours sensors only for WGT
    if has_heating:
        entities.extend([
            OperatingHoursSensor(coordinator, entry, "operating_hours_heat_pump"),
            OperatingHoursSensor(coordinator, entry, "operating_hours_heat_pump_cooling",),
            OperatingHoursSensor(coordinator, entry, "operating_hours_vhr"),
            OperatingHoursSensor(coordinator, entry, "operating_hours_auxiliary_heating_house"),
            OperatingHoursSensor(coordinator, entry, "operating_hours_ewt"),
        ])

    async_add_entities(entities)


class SensorBase(CoordinatorEntity[Coordinator], SensorEntity):
    """Base class for WRG sensors."""

    _attr_has_entity_name = True

    def __init__(
        self,
        coordinator: Coordinator,
        entry: ConfigEntry,
        key: str,
        name: str,
    ) -> None:
        """Initialize the sensor."""
        super().__init__(coordinator)
        self._key = key
        self._attr_name = name
        self._attr_unique_id = f"{entry.entry_id}_{key}"

        model = MODEL_WGT if coordinator.has_heating() else MODEL_WRT
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, entry.entry_id)},
            name="Lüftung",
            manufacturer=MANUFACTURER,
            model=model,
        )

    @property
    def native_value(self):
        """Return the state of the sensor."""
        return self.coordinator.data.get(self._key)


class CurrentFanLevelSensor(CoordinatorEntity[Coordinator], SensorEntity):
    """Sensor for WRG current fan level (Aktuelle Luftstufe)."""

    _attr_has_entity_name = True
    _attr_translation_key = "current_fan_level"
    _attr_state_class = SensorStateClass.MEASUREMENT

    def __init__(
        self,
        coordinator: Coordinator,
        entry: ConfigEntry,
    ) -> None:
        """Initialize the sensor."""
        super().__init__(coordinator)
        self._attr_unique_id = f"{entry.entry_id}_current_fan_level"

        model = MODEL_WGT if coordinator.has_heating() else MODEL_WRT
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, entry.entry_id)},
            name="Lüftung",
            manufacturer=MANUFACTURER,
            model=model,
        )

    @property
    def native_value(self) -> int | None:
        """Return the current fan level as number (0-4)."""
        return self.coordinator.data.get("current_fan_level")


class TimeProgramBaseLevelSensor(CoordinatorEntity[Coordinator], SensorEntity):
    """Sensor for WRG time program base level (Zeitprogramm Basis Luftstufe)."""

    _attr_has_entity_name = True
    _attr_translation_key = "time_program_base_level"
    _attr_state_class = SensorStateClass.MEASUREMENT
    _attr_entity_registry_enabled_default = False

    def __init__(
        self,
        coordinator: Coordinator,
        entry: ConfigEntry,
    ) -> None:
        """Initialize the sensor."""
        super().__init__(coordinator)
        self._attr_unique_id = f"{entry.entry_id}_time_program_base_level"

        model = MODEL_WGT if coordinator.has_heating() else MODEL_WRT
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, entry.entry_id)},
            name="Lüftung",
            manufacturer=MANUFACTURER,
            model=model,
        )

    @property
    def native_value(self) -> int | None:
        """Return the time program base level as number (0-4)."""
        return self.coordinator.data.get("time_program_base_level")


class ShockVentilationRemainingSensor(CoordinatorEntity[Coordinator], SensorEntity):
    """Sensor for WRG shock ventilation remaining time (Restlaufzeit Stoßlüftung)."""

    _attr_has_entity_name = True
    _attr_translation_key = "shock_ventilation_remaining"
    _attr_device_class = SensorDeviceClass.DURATION
    _attr_native_unit_of_measurement = UnitOfTime.MINUTES

    def __init__(
        self,
        coordinator: Coordinator,
        entry: ConfigEntry,
    ) -> None:
        """Initialize the sensor."""
        super().__init__(coordinator)
        self._attr_unique_id = f"{entry.entry_id}_shock_ventilation_remaining"

        model = MODEL_WGT if coordinator.has_heating() else MODEL_WRT
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, entry.entry_id)},
            name="Lüftung",
            manufacturer=MANUFACTURER,
            model=model,
        )

    @property
    def native_value(self) -> int | None:
        """Return the shock ventilation remaining time in minutes."""
        return self.coordinator.data.get("shock_ventilation_remaining")


class HeatPumpStatusSensor(CoordinatorEntity[Coordinator], SensorEntity):
    """Sensor for WRG heat pump status (Status Wärmepumpe)."""

    _attr_has_entity_name = True
    _attr_translation_key = "heat_pump_status"

    def __init__(
        self,
        coordinator: Coordinator,
        entry: ConfigEntry,
    ) -> None:
        """Initialize the sensor."""
        super().__init__(coordinator)
        self._attr_unique_id = f"{entry.entry_id}_heat_pump_status"

        model = MODEL_WGT if coordinator.has_heating() else MODEL_WRT
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, entry.entry_id)},
            name="Lüftung",
            manufacturer=MANUFACTURER,
            model=model,
        )

    @property
    def native_value(self) -> int | None:
        """Return the heat pump status code."""
        return self.coordinator.data.get("heat_pump_status")


class SupplyAirFanStatusSensor(CoordinatorEntity[Coordinator], SensorEntity):
    """Sensor for WRG supply air fan status (Status Gebläse Zuluft)."""

    _attr_has_entity_name = True
    _attr_translation_key = "supply_air_fan_status"
    _attr_entity_registry_enabled_default = False

    def __init__(
        self,
        coordinator: Coordinator,
        entry: ConfigEntry,
    ) -> None:
        """Initialize the sensor."""
        super().__init__(coordinator)
        self._attr_unique_id = f"{entry.entry_id}_supply_air_fan_status"

        model = MODEL_WGT if coordinator.has_heating() else MODEL_WRT
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, entry.entry_id)},
            name="Lüftung",
            manufacturer=MANUFACTURER,
            model=model,
        )

    @property
    def native_value(self) -> int | None:
        """Return the supply air fan status code."""
        return self.coordinator.data.get("supply_air_fan_status")


class ExhaustAirFanStatusSensor(CoordinatorEntity[Coordinator], SensorEntity):
    """Sensor for WRG exhaust air fan status (Status Gebläse Abluft)."""

    _attr_has_entity_name = True
    _attr_translation_key = "exhaust_air_fan_status"
    _attr_entity_registry_enabled_default = False

    def __init__(
        self,
        coordinator: Coordinator,
        entry: ConfigEntry,
    ) -> None:
        """Initialize the sensor."""
        super().__init__(coordinator)
        self._attr_unique_id = f"{entry.entry_id}_exhaust_air_fan_status"

        model = MODEL_WGT if coordinator.has_heating() else MODEL_WRT
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, entry.entry_id)},
            name="Lüftung",
            manufacturer=MANUFACTURER,
            model=model,
        )

    @property
    def native_value(self) -> int | None:
        """Return the exhaust air fan status code."""
        return self.coordinator.data.get("exhaust_air_fan_status")


class EwtStateSensor(CoordinatorEntity[Coordinator], SensorEntity):
    """Sensor for WRG EWT state (EWT Zustand)."""

    _attr_has_entity_name = True
    _attr_translation_key = "ewt_state"
    _attr_entity_registry_enabled_default = False

    def __init__(
        self,
        coordinator: Coordinator,
        entry: ConfigEntry,
    ) -> None:
        """Initialize the sensor."""
        super().__init__(coordinator)
        self._attr_unique_id = f"{entry.entry_id}_ewt_state"

        model = MODEL_WGT if coordinator.has_heating() else MODEL_WRT
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, entry.entry_id)},
            name="Lüftung",
            manufacturer=MANUFACTURER,
            model=model,
        )

    @property
    def native_value(self) -> int | None:
        """Return the EWT state code."""
        return self.coordinator.data.get("ewt_state")


class BypassStateSensor(CoordinatorEntity[Coordinator], SensorEntity):
    """Sensor for WRG bypass state (Bypass Zustand)."""

    _attr_has_entity_name = True
    _attr_translation_key = "bypass_state"

    def __init__(
        self,
        coordinator: Coordinator,
        entry: ConfigEntry,
    ) -> None:
        """Initialize the sensor."""
        super().__init__(coordinator)
        self._attr_unique_id = f"{entry.entry_id}_bypass_state"

        model = MODEL_WGT if coordinator.has_heating() else MODEL_WRT
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, entry.entry_id)},
            name="Lüftung",
            manufacturer=MANUFACTURER,
            model=model,
        )

    @property
    def native_value(self) -> int | None:
        """Return the bypass state code."""
        return self.coordinator.data.get("bypass_state")


class OutdoorDamperStateSensor(CoordinatorEntity[Coordinator], SensorEntity):
    """Sensor for WRG outdoor damper state (Aussenklappe Zustand)."""

    _attr_has_entity_name = True
    _attr_translation_key = "outdoor_damper_state"
    _attr_entity_registry_enabled_default = False

    def __init__(
        self,
        coordinator: Coordinator,
        entry: ConfigEntry,
    ) -> None:
        """Initialize the sensor."""
        super().__init__(coordinator)
        self._attr_unique_id = f"{entry.entry_id}_outdoor_damper_state"

        model = MODEL_WGT if coordinator.has_heating() else MODEL_WRT
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, entry.entry_id)},
            name="Lüftung",
            manufacturer=MANUFACTURER,
            model=model,
        )

    @property
    def native_value(self) -> int | None:
        """Return the outdoor damper state code."""
        return self.coordinator.data.get("outdoor_damper_state")


class TimeProgramFanLevelSensor(CoordinatorEntity[Coordinator], SensorEntity):
    """Sensor for WRG time program fan level (Luftstufe Zeitprogramm)."""

    _attr_has_entity_name = True
    _attr_translation_key = "time_program_fan_level"
    _attr_state_class = SensorStateClass.MEASUREMENT
    _attr_entity_registry_enabled_default = False

    def __init__(
        self,
        coordinator: Coordinator,
        entry: ConfigEntry,
    ) -> None:
        """Initialize the sensor."""
        super().__init__(coordinator)
        self._attr_unique_id = f"{entry.entry_id}_time_program_fan_level"

        model = MODEL_WGT if coordinator.has_heating() else MODEL_WRT
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, entry.entry_id)},
            name="Lüftung",
            manufacturer=MANUFACTURER,
            model=model,
        )

    @property
    def native_value(self) -> int | None:
        """Return the time program fan level as number (0-4)."""
        return self.coordinator.data.get("time_program_fan_level")


class SensorFanLevelSensor(CoordinatorEntity[Coordinator], SensorEntity):
    """Sensor for WRG sensor fan level (Luftstufe Sensoren)."""

    _attr_has_entity_name = True
    _attr_translation_key = "sensor_fan_level"
    _attr_entity_registry_enabled_default = False
    _attr_state_class = SensorStateClass.MEASUREMENT

    def __init__(
        self,
        coordinator: Coordinator,
        entry: ConfigEntry,
    ) -> None:
        """Initialize the sensor."""
        super().__init__(coordinator)
        self._attr_unique_id = f"{entry.entry_id}_sensor_fan_level"

        model = MODEL_WGT if coordinator.has_heating() else MODEL_WRT
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, entry.entry_id)},
            name="Lüftung",
            manufacturer=MANUFACTURER,
            model=model,
        )

    @property
    def native_value(self) -> int | None:
        """Return the sensor fan level as number (0-4)."""
        return self.coordinator.data.get("sensor_fan_level")


class CurrentSupplyAirFlowSensor(CoordinatorEntity[Coordinator], SensorEntity):
    """Sensor for WRG current supply air flow (Luftleistung aktuell Zuluft)."""

    _attr_has_entity_name = True
    _attr_translation_key = "current_supply_air_flow"
    _attr_native_unit_of_measurement = "%"
    _attr_state_class = SensorStateClass.MEASUREMENT
    _attr_entity_registry_enabled_default = False

    def __init__(
        self,
        coordinator: Coordinator,
        entry: ConfigEntry,
    ) -> None:
        """Initialize the sensor."""
        super().__init__(coordinator)
        self._attr_unique_id = f"{entry.entry_id}_current_supply_air_flow"

        model = MODEL_WGT if coordinator.has_heating() else MODEL_WRT
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, entry.entry_id)},
            name="Lüftung",
            manufacturer=MANUFACTURER,
            model=model,
        )

    @property
    def native_value(self) -> int | None:
        """Return the current supply air flow percentage."""
        return self.coordinator.data.get("current_supply_air_flow")


class CurrentExhaustAirFlowSensor(CoordinatorEntity[Coordinator], SensorEntity):
    """Sensor for WRG current exhaust air flow (Luftleistung aktuell Abluft)."""

    _attr_has_entity_name = True
    _attr_translation_key = "current_exhaust_air_flow"
    _attr_native_unit_of_measurement = "%"
    _attr_state_class = SensorStateClass.MEASUREMENT
    _attr_entity_registry_enabled_default = False

    def __init__(
        self,
        coordinator: Coordinator,
        entry: ConfigEntry,
    ) -> None:
        """Initialize the sensor."""
        super().__init__(coordinator)
        self._attr_unique_id = f"{entry.entry_id}_current_exhaust_air_flow"

        model = MODEL_WGT if coordinator.has_heating() else MODEL_WRT
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, entry.entry_id)},
            name="Lüftung",
            manufacturer=MANUFACTURER,
            model=model,
        )

    @property
    def native_value(self) -> int | None:
        """Return the current exhaust air flow percentage."""
        return self.coordinator.data.get("current_exhaust_air_flow")


class CurrentSupplyAirRpmSensor(CoordinatorEntity[Coordinator], SensorEntity):
    """Sensor for WRG current supply air RPM (Aktuelle Drehzahl Zuluft)."""

    _attr_has_entity_name = True
    _attr_translation_key = "current_supply_air_rpm"
    _attr_native_unit_of_measurement = "rpm"
    _attr_state_class = SensorStateClass.MEASUREMENT
    _attr_entity_registry_enabled_default = False

    def __init__(
        self,
        coordinator: Coordinator,
        entry: ConfigEntry,
    ) -> None:
        """Initialize the sensor."""
        super().__init__(coordinator)
        self._attr_unique_id = f"{entry.entry_id}_current_supply_air_rpm"

        model = MODEL_WGT if coordinator.has_heating() else MODEL_WRT
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, entry.entry_id)},
            name="Lüftung",
            manufacturer=MANUFACTURER,
            model=model,
        )

    @property
    def native_value(self) -> int | None:
        """Return the current supply air RPM."""
        return self.coordinator.data.get("current_supply_air_rpm")


class CurrentExhaustAirRpmSensor(CoordinatorEntity[Coordinator], SensorEntity):
    """Sensor for WRG current exhaust air RPM (Aktuelle Drehzahl Abluft)."""

    _attr_has_entity_name = True
    _attr_translation_key = "current_exhaust_air_rpm"
    _attr_native_unit_of_measurement = "rpm"
    _attr_state_class = SensorStateClass.MEASUREMENT
    _attr_entity_registry_enabled_default = False

    def __init__(
        self,
        coordinator: Coordinator,
        entry: ConfigEntry,
    ) -> None:
        """Initialize the sensor."""
        super().__init__(coordinator)
        self._attr_unique_id = f"{entry.entry_id}_current_exhaust_air_rpm"

        model = MODEL_WGT if coordinator.has_heating() else MODEL_WRT
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, entry.entry_id)},
            name="Lüftung",
            manufacturer=MANUFACTURER,
            model=model,
        )

    @property
    def native_value(self) -> int | None:
        """Return the current exhaust air RPM."""
        return self.coordinator.data.get("current_exhaust_air_rpm")


class TemperatureT1AfterEwtSensor(CoordinatorEntity[Coordinator], SensorEntity):
    """Sensor for WRG temperature T1 after EWT (T1 nach EWT)."""

    _attr_has_entity_name = True
    _attr_translation_key = "temperature_t1_after_ewt"
    _attr_native_unit_of_measurement = "°C"
    _attr_device_class = SensorDeviceClass.TEMPERATURE
    _attr_state_class = SensorStateClass.MEASUREMENT
    _attr_entity_registry_enabled_default = False

    def __init__(
        self,
        coordinator: Coordinator,
        entry: ConfigEntry,
    ) -> None:
        """Initialize the sensor."""
        super().__init__(coordinator)
        self._attr_unique_id = f"{entry.entry_id}_temp_t1_after_ewt"

        model = MODEL_WGT if coordinator.has_heating() else MODEL_WRT
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, entry.entry_id)},
            name="Lüftung",
            manufacturer=MANUFACTURER,
            model=model,
        )

    @property
    def native_value(self) -> float | None:
        """Return the temperature T1 after EWT."""
        return self.coordinator.data.get("temp_t1_after_ewt")


class TemperatureT2AfterVhrSensor(CoordinatorEntity[Coordinator], SensorEntity):
    """Sensor for WRG temperature T2 after VHR (T2 nach VHR)."""

    _attr_has_entity_name = True
    _attr_translation_key = "temperature_t2_after_vhr"
    _attr_native_unit_of_measurement = "°C"
    _attr_device_class = SensorDeviceClass.TEMPERATURE
    _attr_state_class = SensorStateClass.MEASUREMENT

    def __init__(
        self,
        coordinator: Coordinator,
        entry: ConfigEntry,
    ) -> None:
        """Initialize the sensor."""
        super().__init__(coordinator)
        self._attr_unique_id = f"{entry.entry_id}_temp_t2_after_vhr"

        model = MODEL_WGT if coordinator.has_heating() else MODEL_WRT
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, entry.entry_id)},
            name="Lüftung",
            manufacturer=MANUFACTURER,
            model=model,
        )

    @property
    def native_value(self) -> float | None:
        """Return the temperature T2 after VHR."""
        return self.coordinator.data.get("temp_t2_after_vhr")


class TemperatureT3BeforeNeSensor(CoordinatorEntity[Coordinator], SensorEntity):
    """Sensor for WRG temperature T3 before NE (T3 vor NE)."""

    _attr_has_entity_name = True
    _attr_translation_key = "temperature_t3_before_ne"
    _attr_native_unit_of_measurement = "°C"
    _attr_device_class = SensorDeviceClass.TEMPERATURE
    _attr_state_class = SensorStateClass.MEASUREMENT

    def __init__(
        self,
        coordinator: Coordinator,
        entry: ConfigEntry,
    ) -> None:
        """Initialize the sensor."""
        super().__init__(coordinator)
        self._attr_unique_id = f"{entry.entry_id}_temp_t3_before_ne"

        model = MODEL_WGT if coordinator.has_heating() else MODEL_WRT
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, entry.entry_id)},
            name="Lüftung",
            manufacturer=MANUFACTURER,
            model=model,
        )

    @property
    def native_value(self) -> float | None:
        """Return the temperature T3 before NE."""
        return self.coordinator.data.get("temp_t3_before_ne")


class TemperatureT4AfterNeSensor(CoordinatorEntity[Coordinator], SensorEntity):
    """Sensor for WRG temperature T4 after NE (T4 nach NE)."""

    _attr_has_entity_name = True
    _attr_translation_key = "temperature_t4_after_ne"
    _attr_native_unit_of_measurement = "°C"
    _attr_device_class = SensorDeviceClass.TEMPERATURE
    _attr_state_class = SensorStateClass.MEASUREMENT

    def __init__(
        self,
        coordinator: Coordinator,
        entry: ConfigEntry,
    ) -> None:
        """Initialize the sensor."""
        super().__init__(coordinator)
        self._attr_unique_id = f"{entry.entry_id}_temp_t4_after_ne"

        model = MODEL_WGT if coordinator.has_heating() else MODEL_WRT
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, entry.entry_id)},
            name="Lüftung",
            manufacturer=MANUFACTURER,
            model=model,
        )

    @property
    def native_value(self) -> float | None:
        """Return the temperature T4 after NE."""
        return self.coordinator.data.get("temp_t4_after_ne")


class TemperatureT5ExhaustAirSensor(CoordinatorEntity[Coordinator], SensorEntity):
    """Sensor for WRG temperature T5 exhaust air (T5 Abluft)."""

    _attr_has_entity_name = True
    _attr_translation_key = "temperature_t5_exhaust_air"
    _attr_native_unit_of_measurement = "°C"
    _attr_device_class = SensorDeviceClass.TEMPERATURE
    _attr_state_class = SensorStateClass.MEASUREMENT

    def __init__(
        self,
        coordinator: Coordinator,
        entry: ConfigEntry,
    ) -> None:
        """Initialize the sensor."""
        super().__init__(coordinator)
        self._attr_unique_id = f"{entry.entry_id}_temp_t5_exhaust_air"

        model = MODEL_WGT if coordinator.has_heating() else MODEL_WRT
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, entry.entry_id)},
            name="Lüftung",
            manufacturer=MANUFACTURER,
            model=model,
        )

    @property
    def native_value(self) -> float | None:
        """Return the temperature T5 exhaust air."""
        return self.coordinator.data.get("temp_t5_exhaust_air")


class TemperatureT6InWtSensor(CoordinatorEntity[Coordinator], SensorEntity):
    """Sensor for WRG temperature T6 in WT (T6 im WT)."""

    _attr_has_entity_name = True
    _attr_translation_key = "temperature_t6_in_wt"
    _attr_native_unit_of_measurement = "°C"
    _attr_device_class = SensorDeviceClass.TEMPERATURE
    _attr_state_class = SensorStateClass.MEASUREMENT

    def __init__(
        self,
        coordinator: Coordinator,
        entry: ConfigEntry,
    ) -> None:
        """Initialize the sensor."""
        super().__init__(coordinator)
        self._attr_unique_id = f"{entry.entry_id}_temp_t6_in_wt"

        model = MODEL_WGT if coordinator.has_heating() else MODEL_WRT
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, entry.entry_id)},
            name="Lüftung",
            manufacturer=MANUFACTURER,
            model=model,
        )

    @property
    def native_value(self) -> float | None:
        """Return the temperature T6 in WT."""
        return self.coordinator.data.get("temp_t6_in_wt")


class TemperatureT7EvaporatorSensor(CoordinatorEntity[Coordinator], SensorEntity):
    """Sensor for WRG temperature T7 evaporator (T7 Verdampfer)."""

    _attr_has_entity_name = True
    _attr_translation_key = "temperature_t7_evaporator"
    _attr_native_unit_of_measurement = "°C"
    _attr_device_class = SensorDeviceClass.TEMPERATURE
    _attr_state_class = SensorStateClass.MEASUREMENT

    def __init__(
        self,
        coordinator: Coordinator,
        entry: ConfigEntry,
    ) -> None:
        """Initialize the sensor."""
        super().__init__(coordinator)
        self._attr_unique_id = f"{entry.entry_id}_temp_t7_evaporator"

        model = MODEL_WGT if coordinator.has_heating() else MODEL_WRT
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, entry.entry_id)},
            name="Lüftung",
            manufacturer=MANUFACTURER,
            model=model,
        )

    @property
    def native_value(self) -> float | None:
        """Return the temperature T7 evaporator."""
        return self.coordinator.data.get("temp_t7_evaporator")


class TemperatureT8CondenserSensor(CoordinatorEntity[Coordinator], SensorEntity):
    """Sensor for WRG temperature T8 condenser (T8 Kondensator)."""

    _attr_has_entity_name = True
    _attr_translation_key = "temperature_t8_condenser"
    _attr_native_unit_of_measurement = "°C"
    _attr_device_class = SensorDeviceClass.TEMPERATURE
    _attr_state_class = SensorStateClass.MEASUREMENT

    def __init__(
        self,
        coordinator: Coordinator,
        entry: ConfigEntry,
    ) -> None:
        """Initialize the sensor."""
        super().__init__(coordinator)
        self._attr_unique_id = f"{entry.entry_id}_temp_t8_condenser"

        model = MODEL_WGT if coordinator.has_heating() else MODEL_WRT
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, entry.entry_id)},
            name="Lüftung",
            manufacturer=MANUFACTURER,
            model=model,
        )

    @property
    def native_value(self) -> float | None:
        """Return the temperature T8 condenser."""
        return self.coordinator.data.get("temp_t8_condenser")


class TemperatureT10OutdoorSensor(CoordinatorEntity[Coordinator], SensorEntity):
    """Sensor for WRG temperature T10 outdoor (T10 Aussen)."""

    _attr_has_entity_name = True
    _attr_translation_key = "temperature_t10_outdoor"
    _attr_native_unit_of_measurement = "°C"
    _attr_device_class = SensorDeviceClass.TEMPERATURE
    _attr_state_class = SensorStateClass.MEASUREMENT

    def __init__(
        self,
        coordinator: Coordinator,
        entry: ConfigEntry,
    ) -> None:
        """Initialize the sensor."""
        super().__init__(coordinator)
        self._attr_unique_id = f"{entry.entry_id}_temp_t10_outdoor"

        model = MODEL_WGT if coordinator.has_heating() else MODEL_WRT
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, entry.entry_id)},
            name="Lüftung",
            manufacturer=MANUFACTURER,
            model=model,
        )

    @property
    def native_value(self) -> float | None:
        """Return the temperature T10 outdoor."""
        return self.coordinator.data.get("temp_t10_outdoor")


class DeviceFilterRemainingSensor(CoordinatorEntity[Coordinator], SensorEntity):
    """Sensor for WRG device filter remaining days (Restlaufzeit Gerätefilter)."""

    _attr_has_entity_name = True
    _attr_translation_key = "device_filter_remaining"
    _attr_device_class = SensorDeviceClass.DURATION
    _attr_native_unit_of_measurement = UnitOfTime.DAYS

    def __init__(
        self,
        coordinator: Coordinator,
        entry: ConfigEntry,
    ) -> None:
        """Initialize the sensor."""
        super().__init__(coordinator)
        self._attr_unique_id = f"{entry.entry_id}_device_filter_remaining"

        model = MODEL_WGT if coordinator.has_heating() else MODEL_WRT
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, entry.entry_id)},
            name="Lüftung",
            manufacturer=MANUFACTURER,
            model=model,
        )

    @property
    def native_value(self) -> int | None:
        """Return the device filter remaining days."""
        return self.coordinator.data.get("device_filter_remaining")


class UpstreamFilterRemainingSensor(CoordinatorEntity[Coordinator], SensorEntity):
    """Sensor for WRG upstream filter remaining days.

    Restlaufzeit Vorgelagerter Filter.
    """

    _attr_has_entity_name = True
    _attr_translation_key = "upstream_filter_remaining"
    _attr_device_class = SensorDeviceClass.DURATION
    _attr_native_unit_of_measurement = UnitOfTime.DAYS

    def __init__(
        self,
        coordinator: Coordinator,
        entry: ConfigEntry,
    ) -> None:
        """Initialize the sensor."""
        super().__init__(coordinator)
        self._attr_unique_id = f"{entry.entry_id}_upstream_filter_remaining"

        model = MODEL_WGT if coordinator.has_heating() else MODEL_WRT
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, entry.entry_id)},
            name="Lüftung",
            manufacturer=MANUFACTURER,
            model=model,
        )

    @property
    def native_value(self) -> int | None:
        """Return the upstream filter remaining days."""
        return self.coordinator.data.get("upstream_filter_remaining")


class ErrorMessageSensor(CoordinatorEntity[Coordinator], SensorEntity):
    """Sensor for WRG error message."""

    _attr_has_entity_name = True
    _attr_translation_key = "error_message"

    def __init__(
        self,
        coordinator: Coordinator,
        entry: ConfigEntry,
    ) -> None:
        """Initialize the sensor."""
        super().__init__(coordinator)
        self._attr_unique_id = f"{entry.entry_id}_error_message"

        model = MODEL_WGT if coordinator.has_heating() else MODEL_WRT
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, entry.entry_id)},
            name="Lüftung",
            manufacturer=MANUFACTURER,
            model=model,
        )

    @property
    def native_value(self) -> int | None:
        """Return the error code as number."""
        return self.coordinator.data.get("error_message")


class RoomAuxiliaryHeatingSensor(CoordinatorEntity[Coordinator], SensorEntity):
    """Sensor for room auxiliary heating release."""

    _attr_entity_registry_enabled_default = False

    def __init__(
        self,
        coordinator: Coordinator,
        room_number: int,
        room_name: str,
    ) -> None:
        """Initialize the sensor."""
        super().__init__(coordinator)
        self._room_number = room_number
        self._room_name = room_name
        entry_id = coordinator.config_entry.entry_id
        self._attr_unique_id = (
            f"{entry_id}_room_{room_number}_auxiliary_heating"
        )
        self._attr_translation_key = "auxiliary_heating_release"

        # Room-specific device
        self._attr_device_info = {
            "identifiers": {
                (DOMAIN, f"{entry_id}_room_{room_number}")
            },
            "name": room_name,
            "manufacturer": MANUFACTURER,
            "model": "Room Climate Control",
            "via_device": (DOMAIN, coordinator.config_entry.entry_id),
        }

    @property
    def native_value(self) -> str | None:
        """Return the auxiliary heating status."""
        # Register 440-456 for rooms 1-17
        value = self.coordinator.data.get(f"heating_enable_{self._room_number}")
        if value == 0:
            return "Blocked"
        elif value == 1:
            return "Heating Enabled"
        return None

class RoomTemperatureSensor(CoordinatorEntity[Coordinator], SensorEntity):
    """Sensor for room temperature."""

    _attr_device_class = SensorDeviceClass.TEMPERATURE
    _attr_state_class = SensorStateClass.MEASUREMENT
    _attr_native_unit_of_measurement = UnitOfTemperature.CELSIUS
    _attr_has_entity_name = True

    def __init__(
        self,
        coordinator: Coordinator,
        room_number: int,
        room_name: str,
    ) -> None:
        """Initialize the sensor."""
        super().__init__(coordinator)
        self._room_number = room_number
        self._room_name = room_name
        entry_id = coordinator.config_entry.entry_id
        self._attr_unique_id = f"{entry_id}_room_{room_number}_temperature"
        self._attr_translation_key = "room_temperature"

        # Room-specific device
        self._attr_device_info = {
            "identifiers": {(DOMAIN, f"{entry_id}_room_{room_number}")},
            "name": room_name,
            "manufacturer": MANUFACTURER,
            "model": "Room Temperature",
            "via_device": (DOMAIN, coordinator.config_entry.entry_id),
        }

    @property
    def native_value(self) -> float | None:
        """Return the room temperature."""
        # Register 360-376 for rooms 1-17
        return self.coordinator.data.get(f"current_temp_temperature_{self._room_number}")


class OperatingHoursSensor(CoordinatorEntity[Coordinator], SensorEntity):
    """Sensor for operating hours."""

    _attr_device_class = SensorDeviceClass.DURATION
    _attr_state_class = SensorStateClass.TOTAL_INCREASING
    _attr_native_unit_of_measurement = UnitOfTime.HOURS
    _attr_has_entity_name = True
    _attr_entity_registry_enabled_default = False

    def __init__(
        self,
        coordinator: Coordinator,
        entry: ConfigEntry,
        key: str,
    ) -> None:
        """Initialize the sensor."""
        super().__init__(coordinator)
        self._key = key
        self._attr_unique_id = f"{entry.entry_id}_{key}"
        self._attr_translation_key = key

        model = MODEL_WGT if coordinator.has_heating() else MODEL_WRT
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, entry.entry_id)},
            name="Lüftung",
            manufacturer=MANUFACTURER,
            model=model,
        )

    @property
    def native_value(self) -> int | None:
        """Return the operating hours."""
        return self.coordinator.data.get(self._key)


class TemperatureSensor(SensorBase):
    """Temperature sensor."""

    _attr_device_class = SensorDeviceClass.TEMPERATURE
    _attr_state_class = SensorStateClass.MEASUREMENT
    _attr_native_unit_of_measurement = UnitOfTemperature.CELSIUS
