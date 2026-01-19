"""Binary sensor platform for BIC WRG."""
from __future__ import annotations

from homeassistant.components.binary_sensor import (
    BinarySensorDeviceClass,
    BinarySensorEntity,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity import DeviceInfo
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN, MANUFACTURER, MODEL
from .coordinator import BicWrgCoordinator
from .modbus_client import ALARM_ACTIVE


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up WRG binary sensors from a config entry."""
    coordinator: BicWrgCoordinator = hass.data[DOMAIN][entry.entry_id]
    
    entities = [
        BicWrgAlarmBinarySensor(
            coordinator, entry, "alarm_pressure_switch", "Pressure Switch Alarm"
        ),
        BicWrgAlarmBinarySensor(
            coordinator, entry, "alarm_utility_lock", "Utility Lock Alarm"
        ),
        BicWrgAlarmBinarySensor(
            coordinator, entry, "alarm_door_open", "Door Open Alarm"
        ),
        BicWrgAlarmBinarySensor(
            coordinator, entry, "alarm_device_filter_dirty", "Device Filter Dirty Alarm"
        ),
        BicWrgAlarmBinarySensor(
            coordinator, entry, "alarm_upstream_filter_dirty", "Upstream Filter Dirty Alarm"
        ),
        BicWrgAlarmBinarySensor(
            coordinator, entry, "alarm_off_peak_disabled", "Off-Peak Disabled Alarm"
        ),
        BicWrgAlarmBinarySensor(
            coordinator, entry, "alarm_supply_voltage_off", "Supply Voltage Off Alarm"
        ),
        BicWrgAlarmBinarySensor(
            coordinator, entry, "alarm_pressostat_triggered", "Pressostat Triggered Alarm"
        ),
        BicWrgAlarmBinarySensor(
            coordinator, entry, "alarm_external_utility_lock", "External Utility Lock Alarm"
        ),
        BicWrgAlarmBinarySensor(
            coordinator, entry, "alarm_heating_module_test", "Heating Module Test Alarm", enabled_by_default=False
        ),
        BicWrgAlarmBinarySensor(
            coordinator, entry, "alarm_emergency_mode", "Emergency Mode Alarm"
        ),
        BicWrgAlarmBinarySensor(
            coordinator, entry, "alarm_supply_air_cold", "Supply Air Too Cold Alarm"
        ),
    ]
    
    async_add_entities(entities)


class BicWrgAlarmBinarySensor(CoordinatorEntity[BicWrgCoordinator], BinarySensorEntity):
    """Binary sensor for WRG alarms."""

    _attr_has_entity_name = True
    _attr_device_class = BinarySensorDeviceClass.PROBLEM

    def __init__(
        self,
        coordinator: BicWrgCoordinator,
        entry: ConfigEntry,
        key: str,
        name: str,
        enabled_by_default: bool = True,
    ) -> None:
        """Initialize the binary sensor."""
        super().__init__(coordinator)
        self._key = key
        self._attr_name = name
        self._attr_unique_id = f"{entry.entry_id}_{key}"
        self._attr_entity_registry_enabled_default = enabled_by_default
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, entry.entry_id)},
            name="WRG 134-BP-HK",
            manufacturer=MANUFACTURER,
            model=MODEL,
        )

    @property
    def is_on(self) -> bool | None:
        """Return true if the binary sensor is on (alarm active)."""
        value = self.coordinator.data.get(self._key)
        if value is not None:
            return value == ALARM_ACTIVE
        return None
