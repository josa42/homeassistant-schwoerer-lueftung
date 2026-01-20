"""Sensor platform for BIC WRG."""
from __future__ import annotations

from homeassistant.components.sensor import (
    SensorDeviceClass,
    SensorEntity,
    SensorStateClass,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import UnitOfTemperature, UnitOfTime
from homeassistant.components.sensor import SensorDeviceClass as SDC
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity import DeviceInfo
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity
from typing import Any

from .const import DOMAIN, MANUFACTURER, MODEL, CONF_ROOMS
from .coordinator import BicWrgCoordinator
from .modbus_client import (
    HEAT_PUMP_STATUS_OFF,
    HEAT_PUMP_STATUS_HEATING,
    HEAT_PUMP_STATUS_COOLING,
    SUPPLY_AIR_FAN_STATUS_DISABLED,
    SUPPLY_AIR_FAN_STATUS_STARTUP,
    SUPPLY_AIR_FAN_STATUS_ACTIVE,
    SUPPLY_AIR_FAN_STATUS_STANDBY,
    SUPPLY_AIR_FAN_STATUS_ERROR,
    EXHAUST_AIR_FAN_STATUS_DISABLED,
    EXHAUST_AIR_FAN_STATUS_STARTUP,
    EXHAUST_AIR_FAN_STATUS_ACTIVE,
    EXHAUST_AIR_FAN_STATUS_STANDBY,
    EXHAUST_AIR_FAN_STATUS_ERROR,
    EWT_STATE_OFF,
    EWT_STATE_HEATING,
    EWT_STATE_COOLING,
    BYPASS_STATE_CLOSED,
    BYPASS_STATE_OPEN_COOLING,
    BYPASS_STATE_OPEN_HEATING,
    OUTDOOR_DAMPER_STATE_CLOSED,
    OUTDOOR_DAMPER_STATE_OPEN,
    ERROR_CODES,
)

# Current fan level is now numeric (0-4)
# Time program base level is now numeric (0-4)
# Time program fan level is now numeric (0-4)
# Sensor fan level is now numeric (0-4)

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
    """Set up WRG sensors from a config entry."""
    coordinator: BicWrgCoordinator = hass.data[DOMAIN][entry.entry_id]
    rooms: list[dict[str, Any]] = entry.data.get(CONF_ROOMS, [])
    
    entities = [
        BicWrgCurrentFanLevelSensor(coordinator, entry),
        BicWrgTimeProgramBaseLevelSensor(coordinator, entry),
        BicWrgShockVentilationRemainingSensor(coordinator, entry),
        BicWrgHeatPumpStatusSensor(coordinator, entry),
        BicWrgSupplyAirFanStatusSensor(coordinator, entry),
        BicWrgExhaustAirFanStatusSensor(coordinator, entry),
        BicWrgEwtStateSensor(coordinator, entry),
        BicWrgBypassStateSensor(coordinator, entry),
        BicWrgOutdoorDamperStateSensor(coordinator, entry),
        BicWrgTimeProgramFanLevelSensor(coordinator, entry),
        BicWrgSensorFanLevelSensor(coordinator, entry),
        BicWrgCurrentSupplyAirFlowSensor(coordinator, entry),
        BicWrgCurrentExhaustAirFlowSensor(coordinator, entry),
        BicWrgCurrentSupplyAirRpmSensor(coordinator, entry),
        BicWrgCurrentExhaustAirRpmSensor(coordinator, entry),
        BicWrgTemperatureT1AfterEwtSensor(coordinator, entry),
        BicWrgTemperatureT2AfterVhrSensor(coordinator, entry),
        BicWrgTemperatureT3BeforeNeSensor(coordinator, entry),
        BicWrgTemperatureT4AfterNeSensor(coordinator, entry),
        BicWrgTemperatureT5ExhaustAirSensor(coordinator, entry),
        BicWrgTemperatureT6InWtSensor(coordinator, entry),
        BicWrgTemperatureT7EvaporatorSensor(coordinator, entry),
        BicWrgTemperatureT8CondenserSensor(coordinator, entry),
        BicWrgTemperatureT10OutdoorSensor(coordinator, entry),
        BicWrgDeviceFilterRemainingSensor(coordinator, entry),
        BicWrgUpstreamFilterRemainingSensor(coordinator, entry),
        BicWrgErrorMessageSensor(coordinator, entry),
    ]
    
    # Add room-specific sensors
    for room in rooms:
        entities.append(
            BicWrgRoomAuxiliaryHeatingSensor(coordinator, room["number"], room["name"])
        )
    
    # Add operating hours sensors
    entities.extend([
        BicWrgOperatingHoursSensor(coordinator, entry, "fan", 800, "operating_hours_fan"),
        BicWrgOperatingHoursSensor(coordinator, entry, "fan_level_1", 801, "operating_hours_fan_level_1"),
        BicWrgOperatingHoursSensor(coordinator, entry, "fan_level_2", 802, "operating_hours_fan_level_2"),
        BicWrgOperatingHoursSensor(coordinator, entry, "fan_level_3", 803, "operating_hours_fan_level_3"),
        BicWrgOperatingHoursSensor(coordinator, entry, "fan_level_4", 804, "operating_hours_fan_level_4"),
        BicWrgOperatingHoursSensor(coordinator, entry, "heat_pump", 805, "operating_hours_heat_pump"),
        BicWrgOperatingHoursSensor(coordinator, entry, "heat_pump_cooling", 806, "operating_hours_heat_pump_cooling"),
        BicWrgOperatingHoursSensor(coordinator, entry, "vhr", 809, "operating_hours_vhr"),
        BicWrgOperatingHoursSensor(coordinator, entry, "auxiliary_heating_house", 810, "operating_hours_auxiliary_heating_house"),
        BicWrgOperatingHoursSensor(coordinator, entry, "ewt", 813, "operating_hours_ewt"),
    ])
    
    async_add_entities(entities)


class BicWrgSensorBase(CoordinatorEntity[BicWrgCoordinator], SensorEntity):
    """Base class for WRG sensors."""

    _attr_has_entity_name = True

    def __init__(
        self,
        coordinator: BicWrgCoordinator,
        entry: ConfigEntry,
        key: str,
        name: str,
    ) -> None:
        """Initialize the sensor."""
        super().__init__(coordinator)
        self._key = key
        self._attr_name = name
        self._attr_unique_id = f"{entry.entry_id}_{key}"
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, entry.entry_id)},
            name="WRG 134-BP-HK",
            manufacturer=MANUFACTURER,
            model=MODEL,
        )

    @property
    def native_value(self):
        """Return the state of the sensor."""
        return self.coordinator.data.get(self._key)


class BicWrgCurrentFanLevelSensor(CoordinatorEntity[BicWrgCoordinator], SensorEntity):
    """Sensor for WRG current fan level (Aktuelle Luftstufe)."""

    _attr_has_entity_name = True
    _attr_translation_key = "current_fan_level"
    _attr_state_class = SensorStateClass.MEASUREMENT

    def __init__(
        self,
        coordinator: BicWrgCoordinator,
        entry: ConfigEntry,
    ) -> None:
        """Initialize the sensor."""
        super().__init__(coordinator)
        self._attr_unique_id = f"{entry.entry_id}_current_fan_level"
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, entry.entry_id)},
            name="WRG 134-BP-HK",
            manufacturer=MANUFACTURER,
            model=MODEL,
        )

    @property
    def native_value(self) -> int | None:
        """Return the current fan level as number (0-4)."""
        return self.coordinator.data.get("current_fan_level")


class BicWrgTimeProgramBaseLevelSensor(CoordinatorEntity[BicWrgCoordinator], SensorEntity):
    """Sensor for WRG time program base level (Zeitprogramm Basis Luftstufe)."""

    _attr_has_entity_name = True
    _attr_translation_key = "time_program_base_level"
    _attr_state_class = SensorStateClass.MEASUREMENT
    _attr_entity_registry_enabled_default = False

    def __init__(
        self,
        coordinator: BicWrgCoordinator,
        entry: ConfigEntry,
    ) -> None:
        """Initialize the sensor."""
        super().__init__(coordinator)
        self._attr_unique_id = f"{entry.entry_id}_time_program_base_level"
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, entry.entry_id)},
            name="WRG 134-BP-HK",
            manufacturer=MANUFACTURER,
            model=MODEL,
        )

    @property
    def native_value(self) -> int | None:
        """Return the time program base level as number (0-4)."""
        return self.coordinator.data.get("time_program_base_level")


class BicWrgShockVentilationRemainingSensor(CoordinatorEntity[BicWrgCoordinator], SensorEntity):
    """Sensor for WRG shock ventilation remaining time (Restlaufzeit Stoßlüftung)."""

    _attr_has_entity_name = True
    _attr_translation_key = "shock_ventilation_remaining"
    _attr_device_class = SensorDeviceClass.DURATION
    _attr_native_unit_of_measurement = UnitOfTime.MINUTES

    def __init__(
        self,
        coordinator: BicWrgCoordinator,
        entry: ConfigEntry,
    ) -> None:
        """Initialize the sensor."""
        super().__init__(coordinator)
        self._attr_unique_id = f"{entry.entry_id}_shock_ventilation_remaining"
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, entry.entry_id)},
            name="WRG 134-BP-HK",
            manufacturer=MANUFACTURER,
            model=MODEL,
        )

    @property
    def native_value(self) -> int | None:
        """Return the shock ventilation remaining time in minutes."""
        return self.coordinator.data.get("shock_ventilation_remaining")


class BicWrgHeatPumpStatusSensor(CoordinatorEntity[BicWrgCoordinator], SensorEntity):
    """Sensor for WRG heat pump status (Status Wärmepumpe)."""

    _attr_has_entity_name = True
    _attr_translation_key = "heat_pump_status"

    def __init__(
        self,
        coordinator: BicWrgCoordinator,
        entry: ConfigEntry,
    ) -> None:
        """Initialize the sensor."""
        super().__init__(coordinator)
        self._attr_unique_id = f"{entry.entry_id}_heat_pump_status"
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, entry.entry_id)},
            name="WRG 134-BP-HK",
            manufacturer=MANUFACTURER,
            model=MODEL,
        )

    @property
    def native_value(self) -> str | None:
        """Return the heat pump status as text."""
        status = self.coordinator.data.get("heat_pump_status")
        if status is not None and status in HEAT_PUMP_STATUSES:
            return HEAT_PUMP_STATUSES[status]
        return None


class BicWrgSupplyAirFanStatusSensor(CoordinatorEntity[BicWrgCoordinator], SensorEntity):
    """Sensor for WRG supply air fan status (Status Gebläse Zuluft)."""

    _attr_has_entity_name = True
    _attr_translation_key = "supply_air_fan_status"
    _attr_entity_registry_enabled_default = False

    def __init__(
        self,
        coordinator: BicWrgCoordinator,
        entry: ConfigEntry,
    ) -> None:
        """Initialize the sensor."""
        super().__init__(coordinator)
        self._attr_unique_id = f"{entry.entry_id}_supply_air_fan_status"
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, entry.entry_id)},
            name="WRG 134-BP-HK",
            manufacturer=MANUFACTURER,
            model=MODEL,
        )

    @property
    def native_value(self) -> str | None:
        """Return the supply air fan status as text."""
        status = self.coordinator.data.get("supply_air_fan_status")
        if status is not None and status in SUPPLY_AIR_FAN_STATUSES:
            return SUPPLY_AIR_FAN_STATUSES[status]
        return None


class BicWrgExhaustAirFanStatusSensor(CoordinatorEntity[BicWrgCoordinator], SensorEntity):
    """Sensor for WRG exhaust air fan status (Status Gebläse Abluft)."""

    _attr_has_entity_name = True
    _attr_translation_key = "exhaust_air_fan_status"
    _attr_entity_registry_enabled_default = False

    def __init__(
        self,
        coordinator: BicWrgCoordinator,
        entry: ConfigEntry,
    ) -> None:
        """Initialize the sensor."""
        super().__init__(coordinator)
        self._attr_unique_id = f"{entry.entry_id}_exhaust_air_fan_status"
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, entry.entry_id)},
            name="WRG 134-BP-HK",
            manufacturer=MANUFACTURER,
            model=MODEL,
        )

    @property
    def native_value(self) -> str | None:
        """Return the exhaust air fan status as text."""
        status = self.coordinator.data.get("exhaust_air_fan_status")
        if status is not None and status in EXHAUST_AIR_FAN_STATUSES:
            return EXHAUST_AIR_FAN_STATUSES[status]
        return None


class BicWrgEwtStateSensor(CoordinatorEntity[BicWrgCoordinator], SensorEntity):
    """Sensor for WRG EWT state (EWT Zustand)."""

    _attr_has_entity_name = True
    _attr_translation_key = "ewt_state"
    _attr_entity_registry_enabled_default = False

    def __init__(
        self,
        coordinator: BicWrgCoordinator,
        entry: ConfigEntry,
    ) -> None:
        """Initialize the sensor."""
        super().__init__(coordinator)
        self._attr_unique_id = f"{entry.entry_id}_ewt_state"
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, entry.entry_id)},
            name="WRG 134-BP-HK",
            manufacturer=MANUFACTURER,
            model=MODEL,
        )

    @property
    def native_value(self) -> str | None:
        """Return the EWT state as text."""
        state = self.coordinator.data.get("ewt_state")
        if state is not None and state in EWT_STATES:
            return EWT_STATES[state]
        return None


class BicWrgBypassStateSensor(CoordinatorEntity[BicWrgCoordinator], SensorEntity):
    """Sensor for WRG bypass state (Bypass Zustand)."""

    _attr_has_entity_name = True
    _attr_translation_key = "bypass_state"

    def __init__(
        self,
        coordinator: BicWrgCoordinator,
        entry: ConfigEntry,
    ) -> None:
        """Initialize the sensor."""
        super().__init__(coordinator)
        self._attr_unique_id = f"{entry.entry_id}_bypass_state"
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, entry.entry_id)},
            name="WRG 134-BP-HK",
            manufacturer=MANUFACTURER,
            model=MODEL,
        )

    @property
    def native_value(self) -> str | None:
        """Return the bypass state as text."""
        state = self.coordinator.data.get("bypass_state")
        if state is not None and state in BYPASS_STATES:
            return BYPASS_STATES[state]
        return None


class BicWrgOutdoorDamperStateSensor(CoordinatorEntity[BicWrgCoordinator], SensorEntity):
    """Sensor for WRG outdoor damper state (Aussenklappe Zustand)."""

    _attr_has_entity_name = True
    _attr_translation_key = "outdoor_damper_state"
    _attr_entity_registry_enabled_default = False

    def __init__(
        self,
        coordinator: BicWrgCoordinator,
        entry: ConfigEntry,
    ) -> None:
        """Initialize the sensor."""
        super().__init__(coordinator)
        self._attr_unique_id = f"{entry.entry_id}_outdoor_damper_state"
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, entry.entry_id)},
            name="WRG 134-BP-HK",
            manufacturer=MANUFACTURER,
            model=MODEL,
        )

    @property
    def native_value(self) -> str | None:
        """Return the outdoor damper state as text."""
        state = self.coordinator.data.get("outdoor_damper_state")
        if state is not None and state in OUTDOOR_DAMPER_STATES:
            return OUTDOOR_DAMPER_STATES[state]
        return None


class BicWrgTimeProgramFanLevelSensor(CoordinatorEntity[BicWrgCoordinator], SensorEntity):
    """Sensor for WRG time program fan level (Luftstufe Zeitprogramm)."""

    _attr_has_entity_name = True
    _attr_translation_key = "time_program_fan_level"
    _attr_state_class = SensorStateClass.MEASUREMENT

    def __init__(
        self,
        coordinator: BicWrgCoordinator,
        entry: ConfigEntry,
    ) -> None:
        """Initialize the sensor."""
        super().__init__(coordinator)
        self._attr_unique_id = f"{entry.entry_id}_time_program_fan_level"
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, entry.entry_id)},
            name="WRG 134-BP-HK",
            manufacturer=MANUFACTURER,
            model=MODEL,
        )

    @property
    def native_value(self) -> int | None:
        """Return the time program fan level as number (0-4)."""
        return self.coordinator.data.get("time_program_fan_level")


class BicWrgSensorFanLevelSensor(CoordinatorEntity[BicWrgCoordinator], SensorEntity):
    """Sensor for WRG sensor fan level (Luftstufe Sensoren)."""

    _attr_has_entity_name = True
    _attr_translation_key = "sensor_fan_level"
    _attr_entity_registry_enabled_default = False
    _attr_state_class = SensorStateClass.MEASUREMENT

    def __init__(
        self,
        coordinator: BicWrgCoordinator,
        entry: ConfigEntry,
    ) -> None:
        """Initialize the sensor."""
        super().__init__(coordinator)
        self._attr_unique_id = f"{entry.entry_id}_sensor_fan_level"
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, entry.entry_id)},
            name="WRG 134-BP-HK",
            manufacturer=MANUFACTURER,
            model=MODEL,
        )

    @property
    def native_value(self) -> int | None:
        """Return the sensor fan level as number (0-4)."""
        return self.coordinator.data.get("sensor_fan_level")


class BicWrgCurrentSupplyAirFlowSensor(CoordinatorEntity[BicWrgCoordinator], SensorEntity):
    """Sensor for WRG current supply air flow (Luftleistung aktuell Zuluft)."""

    _attr_has_entity_name = True
    _attr_translation_key = "current_supply_air_flow"
    _attr_native_unit_of_measurement = "%"
    _attr_state_class = SensorStateClass.MEASUREMENT
    _attr_entity_registry_enabled_default = False

    def __init__(
        self,
        coordinator: BicWrgCoordinator,
        entry: ConfigEntry,
    ) -> None:
        """Initialize the sensor."""
        super().__init__(coordinator)
        self._attr_unique_id = f"{entry.entry_id}_current_supply_air_flow"
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, entry.entry_id)},
            name="WRG 134-BP-HK",
            manufacturer=MANUFACTURER,
            model=MODEL,
        )

    @property
    def native_value(self) -> int | None:
        """Return the current supply air flow percentage."""
        return self.coordinator.data.get("current_supply_air_flow")


class BicWrgCurrentExhaustAirFlowSensor(CoordinatorEntity[BicWrgCoordinator], SensorEntity):
    """Sensor for WRG current exhaust air flow (Luftleistung aktuell Abluft)."""

    _attr_has_entity_name = True
    _attr_translation_key = "current_exhaust_air_flow"
    _attr_native_unit_of_measurement = "%"
    _attr_state_class = SensorStateClass.MEASUREMENT
    _attr_entity_registry_enabled_default = False

    def __init__(
        self,
        coordinator: BicWrgCoordinator,
        entry: ConfigEntry,
    ) -> None:
        """Initialize the sensor."""
        super().__init__(coordinator)
        self._attr_unique_id = f"{entry.entry_id}_current_exhaust_air_flow"
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, entry.entry_id)},
            name="WRG 134-BP-HK",
            manufacturer=MANUFACTURER,
            model=MODEL,
        )

    @property
    def native_value(self) -> int | None:
        """Return the current exhaust air flow percentage."""
        return self.coordinator.data.get("current_exhaust_air_flow")


class BicWrgCurrentSupplyAirRpmSensor(CoordinatorEntity[BicWrgCoordinator], SensorEntity):
    """Sensor for WRG current supply air RPM (Aktuelle Drehzahl Zuluft)."""

    _attr_has_entity_name = True
    _attr_translation_key = "current_supply_air_rpm"
    _attr_native_unit_of_measurement = "rpm"
    _attr_state_class = SensorStateClass.MEASUREMENT
    _attr_entity_registry_enabled_default = False

    def __init__(
        self,
        coordinator: BicWrgCoordinator,
        entry: ConfigEntry,
    ) -> None:
        """Initialize the sensor."""
        super().__init__(coordinator)
        self._attr_unique_id = f"{entry.entry_id}_current_supply_air_rpm"
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, entry.entry_id)},
            name="WRG 134-BP-HK",
            manufacturer=MANUFACTURER,
            model=MODEL,
        )

    @property
    def native_value(self) -> int | None:
        """Return the current supply air RPM."""
        return self.coordinator.data.get("current_supply_air_rpm")


class BicWrgCurrentExhaustAirRpmSensor(CoordinatorEntity[BicWrgCoordinator], SensorEntity):
    """Sensor for WRG current exhaust air RPM (Aktuelle Drehzahl Abluft)."""

    _attr_has_entity_name = True
    _attr_translation_key = "current_exhaust_air_rpm"
    _attr_native_unit_of_measurement = "rpm"
    _attr_state_class = SensorStateClass.MEASUREMENT
    _attr_entity_registry_enabled_default = False

    def __init__(
        self,
        coordinator: BicWrgCoordinator,
        entry: ConfigEntry,
    ) -> None:
        """Initialize the sensor."""
        super().__init__(coordinator)
        self._attr_unique_id = f"{entry.entry_id}_current_exhaust_air_rpm"
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, entry.entry_id)},
            name="WRG 134-BP-HK",
            manufacturer=MANUFACTURER,
            model=MODEL,
        )

    @property
    def native_value(self) -> int | None:
        """Return the current exhaust air RPM."""
        return self.coordinator.data.get("current_exhaust_air_rpm")


class BicWrgTemperatureT1AfterEwtSensor(CoordinatorEntity[BicWrgCoordinator], SensorEntity):
    """Sensor for WRG temperature T1 after EWT (T1 nach EWT)."""

    _attr_has_entity_name = True
    _attr_translation_key = "temperature_t1_after_ewt"
    _attr_native_unit_of_measurement = "°C"
    _attr_device_class = SensorDeviceClass.TEMPERATURE
    _attr_state_class = SensorStateClass.MEASUREMENT
    _attr_entity_registry_enabled_default = False

    def __init__(
        self,
        coordinator: BicWrgCoordinator,
        entry: ConfigEntry,
    ) -> None:
        """Initialize the sensor."""
        super().__init__(coordinator)
        self._attr_unique_id = f"{entry.entry_id}_temp_t1_after_ewt"
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, entry.entry_id)},
            name="WRG 134-BP-HK",
            manufacturer=MANUFACTURER,
            model=MODEL,
        )

    @property
    def native_value(self) -> float | None:
        """Return the temperature T1 after EWT."""
        return self.coordinator.data.get("temp_t1_after_ewt")


class BicWrgTemperatureT2AfterVhrSensor(CoordinatorEntity[BicWrgCoordinator], SensorEntity):
    """Sensor for WRG temperature T2 after VHR (T2 nach VHR)."""

    _attr_has_entity_name = True
    _attr_translation_key = "temperature_t2_after_vhr"
    _attr_native_unit_of_measurement = "°C"
    _attr_device_class = SensorDeviceClass.TEMPERATURE
    _attr_state_class = SensorStateClass.MEASUREMENT

    def __init__(
        self,
        coordinator: BicWrgCoordinator,
        entry: ConfigEntry,
    ) -> None:
        """Initialize the sensor."""
        super().__init__(coordinator)
        self._attr_unique_id = f"{entry.entry_id}_temp_t2_after_vhr"
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, entry.entry_id)},
            name="WRG 134-BP-HK",
            manufacturer=MANUFACTURER,
            model=MODEL,
        )

    @property
    def native_value(self) -> float | None:
        """Return the temperature T2 after VHR."""
        return self.coordinator.data.get("temp_t2_after_vhr")


class BicWrgTemperatureT3BeforeNeSensor(CoordinatorEntity[BicWrgCoordinator], SensorEntity):
    """Sensor for WRG temperature T3 before NE (T3 vor NE)."""

    _attr_has_entity_name = True
    _attr_translation_key = "temperature_t3_before_ne"
    _attr_native_unit_of_measurement = "°C"
    _attr_device_class = SensorDeviceClass.TEMPERATURE
    _attr_state_class = SensorStateClass.MEASUREMENT

    def __init__(
        self,
        coordinator: BicWrgCoordinator,
        entry: ConfigEntry,
    ) -> None:
        """Initialize the sensor."""
        super().__init__(coordinator)
        self._attr_unique_id = f"{entry.entry_id}_temp_t3_before_ne"
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, entry.entry_id)},
            name="WRG 134-BP-HK",
            manufacturer=MANUFACTURER,
            model=MODEL,
        )

    @property
    def native_value(self) -> float | None:
        """Return the temperature T3 before NE."""
        return self.coordinator.data.get("temp_t3_before_ne")


class BicWrgTemperatureT4AfterNeSensor(CoordinatorEntity[BicWrgCoordinator], SensorEntity):
    """Sensor for WRG temperature T4 after NE (T4 nach NE)."""

    _attr_has_entity_name = True
    _attr_translation_key = "temperature_t4_after_ne"
    _attr_native_unit_of_measurement = "°C"
    _attr_device_class = SensorDeviceClass.TEMPERATURE
    _attr_state_class = SensorStateClass.MEASUREMENT

    def __init__(
        self,
        coordinator: BicWrgCoordinator,
        entry: ConfigEntry,
    ) -> None:
        """Initialize the sensor."""
        super().__init__(coordinator)
        self._attr_unique_id = f"{entry.entry_id}_temp_t4_after_ne"
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, entry.entry_id)},
            name="WRG 134-BP-HK",
            manufacturer=MANUFACTURER,
            model=MODEL,
        )

    @property
    def native_value(self) -> float | None:
        """Return the temperature T4 after NE."""
        return self.coordinator.data.get("temp_t4_after_ne")


class BicWrgTemperatureT5ExhaustAirSensor(CoordinatorEntity[BicWrgCoordinator], SensorEntity):
    """Sensor for WRG temperature T5 exhaust air (T5 Abluft)."""

    _attr_has_entity_name = True
    _attr_translation_key = "temperature_t5_exhaust_air"
    _attr_native_unit_of_measurement = "°C"
    _attr_device_class = SensorDeviceClass.TEMPERATURE
    _attr_state_class = SensorStateClass.MEASUREMENT

    def __init__(
        self,
        coordinator: BicWrgCoordinator,
        entry: ConfigEntry,
    ) -> None:
        """Initialize the sensor."""
        super().__init__(coordinator)
        self._attr_unique_id = f"{entry.entry_id}_temp_t5_exhaust_air"
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, entry.entry_id)},
            name="WRG 134-BP-HK",
            manufacturer=MANUFACTURER,
            model=MODEL,
        )

    @property
    def native_value(self) -> float | None:
        """Return the temperature T5 exhaust air."""
        return self.coordinator.data.get("temp_t5_exhaust_air")


class BicWrgTemperatureT6InWtSensor(CoordinatorEntity[BicWrgCoordinator], SensorEntity):
    """Sensor for WRG temperature T6 in WT (T6 im WT)."""

    _attr_has_entity_name = True
    _attr_translation_key = "temperature_t6_in_wt"
    _attr_native_unit_of_measurement = "°C"
    _attr_device_class = SensorDeviceClass.TEMPERATURE
    _attr_state_class = SensorStateClass.MEASUREMENT

    def __init__(
        self,
        coordinator: BicWrgCoordinator,
        entry: ConfigEntry,
    ) -> None:
        """Initialize the sensor."""
        super().__init__(coordinator)
        self._attr_unique_id = f"{entry.entry_id}_temp_t6_in_wt"
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, entry.entry_id)},
            name="WRG 134-BP-HK",
            manufacturer=MANUFACTURER,
            model=MODEL,
        )

    @property
    def native_value(self) -> float | None:
        """Return the temperature T6 in WT."""
        return self.coordinator.data.get("temp_t6_in_wt")


class BicWrgTemperatureT7EvaporatorSensor(CoordinatorEntity[BicWrgCoordinator], SensorEntity):
    """Sensor for WRG temperature T7 evaporator (T7 Verdampfer)."""

    _attr_has_entity_name = True
    _attr_translation_key = "temperature_t7_evaporator"
    _attr_native_unit_of_measurement = "°C"
    _attr_device_class = SensorDeviceClass.TEMPERATURE
    _attr_state_class = SensorStateClass.MEASUREMENT

    def __init__(
        self,
        coordinator: BicWrgCoordinator,
        entry: ConfigEntry,
    ) -> None:
        """Initialize the sensor."""
        super().__init__(coordinator)
        self._attr_unique_id = f"{entry.entry_id}_temp_t7_evaporator"
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, entry.entry_id)},
            name="WRG 134-BP-HK",
            manufacturer=MANUFACTURER,
            model=MODEL,
        )

    @property
    def native_value(self) -> float | None:
        """Return the temperature T7 evaporator."""
        return self.coordinator.data.get("temp_t7_evaporator")


class BicWrgTemperatureT8CondenserSensor(CoordinatorEntity[BicWrgCoordinator], SensorEntity):
    """Sensor for WRG temperature T8 condenser (T8 Kondensator)."""

    _attr_has_entity_name = True
    _attr_translation_key = "temperature_t8_condenser"
    _attr_native_unit_of_measurement = "°C"
    _attr_device_class = SensorDeviceClass.TEMPERATURE
    _attr_state_class = SensorStateClass.MEASUREMENT

    def __init__(
        self,
        coordinator: BicWrgCoordinator,
        entry: ConfigEntry,
    ) -> None:
        """Initialize the sensor."""
        super().__init__(coordinator)
        self._attr_unique_id = f"{entry.entry_id}_temp_t8_condenser"
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, entry.entry_id)},
            name="WRG 134-BP-HK",
            manufacturer=MANUFACTURER,
            model=MODEL,
        )

    @property
    def native_value(self) -> float | None:
        """Return the temperature T8 condenser."""
        return self.coordinator.data.get("temp_t8_condenser")


class BicWrgTemperatureT10OutdoorSensor(CoordinatorEntity[BicWrgCoordinator], SensorEntity):
    """Sensor for WRG temperature T10 outdoor (T10 Aussen)."""

    _attr_has_entity_name = True
    _attr_translation_key = "temperature_t10_outdoor"
    _attr_native_unit_of_measurement = "°C"
    _attr_device_class = SensorDeviceClass.TEMPERATURE
    _attr_state_class = SensorStateClass.MEASUREMENT

    def __init__(
        self,
        coordinator: BicWrgCoordinator,
        entry: ConfigEntry,
    ) -> None:
        """Initialize the sensor."""
        super().__init__(coordinator)
        self._attr_unique_id = f"{entry.entry_id}_temp_t10_outdoor"
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, entry.entry_id)},
            name="WRG 134-BP-HK",
            manufacturer=MANUFACTURER,
            model=MODEL,
        )

    @property
    def native_value(self) -> float | None:
        """Return the temperature T10 outdoor."""
        return self.coordinator.data.get("temp_t10_outdoor")


class BicWrgDeviceFilterRemainingSensor(CoordinatorEntity[BicWrgCoordinator], SensorEntity):
    """Sensor for WRG device filter remaining days (Restlaufzeit Gerätefilter)."""

    _attr_has_entity_name = True
    _attr_translation_key = "device_filter_remaining"
    _attr_device_class = SensorDeviceClass.DURATION
    _attr_native_unit_of_measurement = UnitOfTime.DAYS

    def __init__(
        self,
        coordinator: BicWrgCoordinator,
        entry: ConfigEntry,
    ) -> None:
        """Initialize the sensor."""
        super().__init__(coordinator)
        self._attr_unique_id = f"{entry.entry_id}_device_filter_remaining"
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, entry.entry_id)},
            name="WRG 134-BP-HK",
            manufacturer=MANUFACTURER,
            model=MODEL,
        )

    @property
    def native_value(self) -> int | None:
        """Return the device filter remaining days."""
        return self.coordinator.data.get("device_filter_remaining")


class BicWrgUpstreamFilterRemainingSensor(CoordinatorEntity[BicWrgCoordinator], SensorEntity):
    """Sensor for WRG upstream filter remaining days (Restlaufzeit Vorgelagerter Filter)."""

    _attr_has_entity_name = True
    _attr_translation_key = "upstream_filter_remaining"
    _attr_device_class = SensorDeviceClass.DURATION
    _attr_native_unit_of_measurement = UnitOfTime.DAYS

    def __init__(
        self,
        coordinator: BicWrgCoordinator,
        entry: ConfigEntry,
    ) -> None:
        """Initialize the sensor."""
        super().__init__(coordinator)
        self._attr_unique_id = f"{entry.entry_id}_upstream_filter_remaining"
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, entry.entry_id)},
            name="WRG 134-BP-HK",
            manufacturer=MANUFACTURER,
            model=MODEL,
        )

    @property
    def native_value(self) -> int | None:
        """Return the upstream filter remaining days."""
        return self.coordinator.data.get("upstream_filter_remaining")


class BicWrgErrorMessageSensor(CoordinatorEntity[BicWrgCoordinator], SensorEntity):
    """Sensor for WRG error message (Fehlermeldung)."""

    _attr_has_entity_name = True
    _attr_translation_key = "error_message"

    def __init__(
        self,
        coordinator: BicWrgCoordinator,
        entry: ConfigEntry,
    ) -> None:
        """Initialize the sensor."""
        super().__init__(coordinator)
        self._attr_unique_id = f"{entry.entry_id}_error_message"
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, entry.entry_id)},
            name="WRG 134-BP-HK",
            manufacturer=MANUFACTURER,
            model=MODEL,
        )

    @property
    def native_value(self) -> str | None:
        """Return the error message as text."""
        error_code = self.coordinator.data.get("error_message")
        if error_code is not None and error_code in ERROR_CODES:
            return ERROR_CODES[error_code]
        if error_code == 0:
            return "No Error"
        return f"Unknown Error ({error_code})"


class BicWrgRoomAuxiliaryHeatingSensor(CoordinatorEntity[BicWrgCoordinator], SensorEntity):
    """Sensor for room auxiliary heating release (Zusatzheizung Freigabe)."""

    _attr_entity_registry_enabled_default = False

    def __init__(
        self,
        coordinator: BicWrgCoordinator,
        room_number: int,
        room_name: str,
    ) -> None:
        """Initialize the sensor."""
        super().__init__(coordinator)
        self._room_number = room_number
        self._room_name = room_name
        self._attr_unique_id = f"{coordinator.config_entry.entry_id}_room_{room_number}_auxiliary_heating"
        self._attr_name = "Auxiliary Heating Release"
        
        # Room-specific device
        self._attr_device_info = {
            "identifiers": {(DOMAIN, f"{coordinator.config_entry.entry_id}_room_{room_number}")},
            "name": room_name,
            "manufacturer": MANUFACTURER,
            "model": "Room Climate Control",
            "via_device": (DOMAIN, coordinator.config_entry.entry_id),
        }

    @property
    def native_value(self) -> str | None:
        """Return the auxiliary heating status."""
        # Register 440-456 for rooms 1-17
        register = 440 + self._room_number - 1
        value = self.coordinator.data.get(f"register_{register}")
        if value == 0:
            return "Blocked"
        elif value == 1:
            return "Heating Enabled"
        return None





class BicWrgOperatingHoursSensor(CoordinatorEntity[BicWrgCoordinator], SensorEntity):
    """Sensor for operating hours (Betriebsstunden)."""

    _attr_device_class = SensorDeviceClass.DURATION
    _attr_state_class = SensorStateClass.TOTAL_INCREASING
    _attr_native_unit_of_measurement = UnitOfTime.HOURS
    _attr_has_entity_name = True
    _attr_entity_registry_enabled_default = False

    def __init__(
        self,
        coordinator: BicWrgCoordinator,
        entry: ConfigEntry,
        key: str,
        register: int,
        translation_key: str,
    ) -> None:
        """Initialize the sensor."""
        super().__init__(coordinator)
        self._key = key
        self._register = register
        self._attr_unique_id = f"{entry.entry_id}_operating_hours_{key}"
        self._attr_translation_key = translation_key
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, entry.entry_id)},
            name="WRG 134-BP-HK",
            manufacturer=MANUFACTURER,
            model=MODEL,
        )

    @property
    def native_value(self) -> int | None:
        """Return the operating hours."""
        return self.coordinator.data.get(f"register_{self._register}")


class BicWrgTemperatureSensor(BicWrgSensorBase):
    """Temperature sensor for WRG."""

    _attr_device_class = SensorDeviceClass.TEMPERATURE
    _attr_state_class = SensorStateClass.MEASUREMENT
    _attr_native_unit_of_measurement = UnitOfTemperature.CELSIUS
