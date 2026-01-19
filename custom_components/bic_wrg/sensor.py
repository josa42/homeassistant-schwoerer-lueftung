"""Sensor platform for BIC WRG."""
from __future__ import annotations

from homeassistant.components.sensor import (
    SensorDeviceClass,
    SensorEntity,
    SensorStateClass,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import UnitOfTemperature, UnitOfTime
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity import DeviceInfo
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN, MANUFACTURER, MODEL
from .coordinator import BicWrgCoordinator
from .modbus_client import (
    CURRENT_FAN_LEVEL_OFF,
    CURRENT_FAN_LEVEL_1,
    CURRENT_FAN_LEVEL_2,
    CURRENT_FAN_LEVEL_3,
    CURRENT_FAN_LEVEL_4,
    FAN_OVERRIDE_INACTIVE,
    FAN_OVERRIDE_ACTIVE,
    TIME_PROGRAM_BASE_LEVEL_OFF,
    TIME_PROGRAM_BASE_LEVEL_1,
    TIME_PROGRAM_BASE_LEVEL_2,
    TIME_PROGRAM_BASE_LEVEL_3,
    TIME_PROGRAM_BASE_LEVEL_4,
    HEAT_PUMP_STATUS_OFF,
    HEAT_PUMP_STATUS_HEATING,
    HEAT_PUMP_STATUS_COOLING,
    NHR_STATE_INACTIVE,
    NHR_STATE_ACTIVE,
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
    PREHEATER_STATE_OFF,
    PREHEATER_STATE_VHR1_ACTIVE,
    PREHEATER_STATE_VHR2_ACTIVE,
    PREHEATER_STATE_VHR1_2_ACTIVE,
    TIME_PROGRAM_FAN_LEVEL_OFF,
    TIME_PROGRAM_FAN_LEVEL_1,
    TIME_PROGRAM_FAN_LEVEL_2,
    TIME_PROGRAM_FAN_LEVEL_3,
    TIME_PROGRAM_FAN_LEVEL_4,
)

# Current fan level mapping
# Aktuelle Luftstufe: 0=Aus, 1=Stufe 1, 2=Stufe 2, 3=Stufe 3, 4=Stufe 4
CURRENT_FAN_LEVELS = {
    CURRENT_FAN_LEVEL_OFF: "Off",
    CURRENT_FAN_LEVEL_1: "Level 1",
    CURRENT_FAN_LEVEL_2: "Level 2",
    CURRENT_FAN_LEVEL_3: "Level 3",
    CURRENT_FAN_LEVEL_4: "Level 4",
}

# Fan override mapping
# Luftstufen Überschreibung: 0=Inaktiv, 1=Aktiv
FAN_OVERRIDE_STATES = {
    FAN_OVERRIDE_INACTIVE: "Inactive",
    FAN_OVERRIDE_ACTIVE: "Active",
}

# Time program base level mapping
# Zeitprogramm Basis Luftstufe: 0=Aus, 1=Stufe 1, 2=Stufe 2, 3=Stufe 3, 4=Stufe 4
TIME_PROGRAM_BASE_LEVELS = {
    TIME_PROGRAM_BASE_LEVEL_OFF: "Off",
    TIME_PROGRAM_BASE_LEVEL_1: "Level 1",
    TIME_PROGRAM_BASE_LEVEL_2: "Level 2",
    TIME_PROGRAM_BASE_LEVEL_3: "Level 3",
    TIME_PROGRAM_BASE_LEVEL_4: "Level 4",
}

# Heat pump status mapping
# Status Wärmepumpe: 0=Aus, 5=WP Heizen, 49=WP Kühlen
HEAT_PUMP_STATUSES = {
    HEAT_PUMP_STATUS_OFF: "Off",
    HEAT_PUMP_STATUS_HEATING: "Heating",
    HEAT_PUMP_STATUS_COOLING: "Cooling",
}

# NHR state mapping
# NHR Zustand: 0=Inaktiv, 1=Aktiv
NHR_STATES = {
    NHR_STATE_INACTIVE: "Inactive",
    NHR_STATE_ACTIVE: "Active",
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

# Preheater state mapping
# Vorheizregister Zustand: 0=Aus, 1=VHR 1 aktiv, 2=VHR 2 aktiv, 3=VHR 1 & 2 aktiv
PREHEATER_STATES = {
    PREHEATER_STATE_OFF: "Off",
    PREHEATER_STATE_VHR1_ACTIVE: "VHR 1 Active",
    PREHEATER_STATE_VHR2_ACTIVE: "VHR 2 Active",
    PREHEATER_STATE_VHR1_2_ACTIVE: "VHR 1 & 2 Active",
}

# Time program fan level mapping
# Luftstufe Zeitprogramm: 0=Aus, 1=Stufe 1, 2=Stufe 2, 3=Stufe 3, 4=Stufe 4
TIME_PROGRAM_FAN_LEVELS = {
    TIME_PROGRAM_FAN_LEVEL_OFF: "Off",
    TIME_PROGRAM_FAN_LEVEL_1: "Level 1",
    TIME_PROGRAM_FAN_LEVEL_2: "Level 2",
    TIME_PROGRAM_FAN_LEVEL_3: "Level 3",
    TIME_PROGRAM_FAN_LEVEL_4: "Level 4",
}


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up WRG sensors from a config entry."""
    coordinator: BicWrgCoordinator = hass.data[DOMAIN][entry.entry_id]
    
    entities = [
        BicWrgCurrentFanLevelSensor(coordinator, entry),
        BicWrgFanOverrideSensor(coordinator, entry),
        BicWrgTimeProgramBaseLevelSensor(coordinator, entry),
        BicWrgShockVentilationRemainingSensor(coordinator, entry),
        BicWrgHeatPumpStatusSensor(coordinator, entry),
        BicWrgNhrStateSensor(coordinator, entry),
        BicWrgSupplyAirFanStatusSensor(coordinator, entry),
        BicWrgExhaustAirFanStatusSensor(coordinator, entry),
        BicWrgEwtStateSensor(coordinator, entry),
        BicWrgBypassStateSensor(coordinator, entry),
        BicWrgOutdoorDamperStateSensor(coordinator, entry),
        BicWrgPreheaterStateSensor(coordinator, entry),
        BicWrgTimeProgramFanLevelSensor(coordinator, entry),
    ]
    
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
    _attr_name = "Current Fan Level"

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
    def native_value(self) -> str | None:
        """Return the current fan level as text."""
        level = self.coordinator.data.get("current_fan_level")
        if level is not None and level in CURRENT_FAN_LEVELS:
            return CURRENT_FAN_LEVELS[level]
        return None


class BicWrgFanOverrideSensor(CoordinatorEntity[BicWrgCoordinator], SensorEntity):
    """Sensor for WRG fan override (Luftstufen Überschreibung)."""

    _attr_has_entity_name = True
    _attr_name = "Fan Override"

    def __init__(
        self,
        coordinator: BicWrgCoordinator,
        entry: ConfigEntry,
    ) -> None:
        """Initialize the sensor."""
        super().__init__(coordinator)
        self._attr_unique_id = f"{entry.entry_id}_fan_override"
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, entry.entry_id)},
            name="WRG 134-BP-HK",
            manufacturer=MANUFACTURER,
            model=MODEL,
        )

    @property
    def native_value(self) -> str | None:
        """Return the fan override state as text."""
        override = self.coordinator.data.get("fan_override")
        if override is not None and override in FAN_OVERRIDE_STATES:
            return FAN_OVERRIDE_STATES[override]
        return None


class BicWrgTimeProgramBaseLevelSensor(CoordinatorEntity[BicWrgCoordinator], SensorEntity):
    """Sensor for WRG time program base level (Zeitprogramm Basis Luftstufe)."""

    _attr_has_entity_name = True
    _attr_name = "Time Program Base Level"

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
    def native_value(self) -> str | None:
        """Return the time program base level as text."""
        level = self.coordinator.data.get("time_program_base_level")
        if level is not None and level in TIME_PROGRAM_BASE_LEVELS:
            return TIME_PROGRAM_BASE_LEVELS[level]
        return None


class BicWrgShockVentilationRemainingSensor(CoordinatorEntity[BicWrgCoordinator], SensorEntity):
    """Sensor for WRG shock ventilation remaining time (Restlaufzeit Stoßlüftung)."""

    _attr_has_entity_name = True
    _attr_name = "Shock Ventilation Remaining"
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
    _attr_name = "Heat Pump Status"

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


class BicWrgNhrStateSensor(CoordinatorEntity[BicWrgCoordinator], SensorEntity):
    """Sensor for WRG NHR state (NHR Zustand)."""

    _attr_has_entity_name = True
    _attr_name = "NHR State"

    def __init__(
        self,
        coordinator: BicWrgCoordinator,
        entry: ConfigEntry,
    ) -> None:
        """Initialize the sensor."""
        super().__init__(coordinator)
        self._attr_unique_id = f"{entry.entry_id}_nhr_state"
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, entry.entry_id)},
            name="WRG 134-BP-HK",
            manufacturer=MANUFACTURER,
            model=MODEL,
        )

    @property
    def native_value(self) -> str | None:
        """Return the NHR state as text."""
        state = self.coordinator.data.get("nhr_state")
        if state is not None and state in NHR_STATES:
            return NHR_STATES[state]
        return None


class BicWrgSupplyAirFanStatusSensor(CoordinatorEntity[BicWrgCoordinator], SensorEntity):
    """Sensor for WRG supply air fan status (Status Gebläse Zuluft)."""

    _attr_has_entity_name = True
    _attr_name = "Supply Air Fan Status"

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
    _attr_name = "Exhaust Air Fan Status"

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
    _attr_name = "EWT State"

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
    _attr_name = "Bypass State"

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
    _attr_name = "Outdoor Damper State"

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


class BicWrgPreheaterStateSensor(CoordinatorEntity[BicWrgCoordinator], SensorEntity):
    """Sensor for WRG preheater state (Vorheizregister Zustand)."""

    _attr_has_entity_name = True
    _attr_name = "Preheater State"

    def __init__(
        self,
        coordinator: BicWrgCoordinator,
        entry: ConfigEntry,
    ) -> None:
        """Initialize the sensor."""
        super().__init__(coordinator)
        self._attr_unique_id = f"{entry.entry_id}_preheater_state"
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, entry.entry_id)},
            name="WRG 134-BP-HK",
            manufacturer=MANUFACTURER,
            model=MODEL,
        )

    @property
    def native_value(self) -> str | None:
        """Return the preheater state as text."""
        state = self.coordinator.data.get("preheater_state")
        if state is not None and state in PREHEATER_STATES:
            return PREHEATER_STATES[state]
        return None


class BicWrgTimeProgramFanLevelSensor(CoordinatorEntity[BicWrgCoordinator], SensorEntity):
    """Sensor for WRG time program fan level (Luftstufe Zeitprogramm)."""

    _attr_has_entity_name = True
    _attr_name = "Time Program Fan Level"

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
    def native_value(self) -> str | None:
        """Return the time program fan level as text."""
        level = self.coordinator.data.get("time_program_fan_level")
        if level is not None and level in TIME_PROGRAM_FAN_LEVELS:
            return TIME_PROGRAM_FAN_LEVELS[level]
        return None


class BicWrgTemperatureSensor(BicWrgSensorBase):
    """Temperature sensor for WRG."""

    _attr_device_class = SensorDeviceClass.TEMPERATURE
    _attr_state_class = SensorStateClass.MEASUREMENT
    _attr_native_unit_of_measurement = UnitOfTemperature.CELSIUS
