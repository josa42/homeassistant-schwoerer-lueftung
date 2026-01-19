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


class BicWrgTemperatureSensor(BicWrgSensorBase):
    """Temperature sensor for WRG."""

    _attr_device_class = SensorDeviceClass.TEMPERATURE
    _attr_state_class = SensorStateClass.MEASUREMENT
    _attr_native_unit_of_measurement = UnitOfTemperature.CELSIUS
