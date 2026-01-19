"""Sensor platform for Bau Info Center WRG."""
from __future__ import annotations

from homeassistant.components.sensor import (
    SensorDeviceClass,
    SensorEntity,
    SensorStateClass,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import UnitOfTemperature
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity import DeviceInfo
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN, MANUFACTURER, MODEL
from .coordinator import BicWrgCoordinator


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up WRG sensors from a config entry."""
    coordinator: BicWrgCoordinator = hass.data[DOMAIN][entry.entry_id]
    
    # TODO: Add actual sensor entities based on available data
    entities = [
        # Example sensors - adjust based on actual device capabilities
        # BicWrgTemperatureSensor(coordinator, entry, "supply_temp", "Supply Temperature"),
        # BicWrgTemperatureSensor(coordinator, entry, "extract_temp", "Extract Temperature"),
        # BicWrgTemperatureSensor(coordinator, entry, "outdoor_temp", "Outdoor Temperature"),
    ]
    
    async_add_entities(entities)


class BicWrgSensorBase(CoordinatorEntity[BicWrgCoordinator], SensorEntity):
    """Base class for WRG sensors."""

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
        self._attr_name = f"WRG {name}"
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


class BicWrgTemperatureSensor(BicWrgSensorBase):
    """Temperature sensor for WRG."""

    _attr_device_class = SensorDeviceClass.TEMPERATURE
    _attr_state_class = SensorStateClass.MEASUREMENT
    _attr_native_unit_of_measurement = UnitOfTemperature.CELSIUS
