"""Binary sensor platform for BIC WRG."""
from __future__ import annotations
import logging

from homeassistant.components.binary_sensor import (
    BinarySensorDeviceClass,
    BinarySensorEntity,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN, MANUFACTURER, MODEL_WGT, MODEL_WRT
from .coordinator import Coordinator
from .modbus_client import (
    ALARM_ACTIVE,
    FAN_OVERRIDE_ACTIVE,
    NHR_STATE_ACTIVE,
    PREHEATER_STATE_VHR1_2_ACTIVE,
    PREHEATER_STATE_VHR1_ACTIVE,
    PREHEATER_STATE_VHR2_ACTIVE,
    REG_FAN_OVERRIDE,
    REG_HEATING_ACTIVE_1,
    REG_NHR_STATE,
)

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up WRG binary sensors from a config entry."""
    coordinator: Coordinator = hass.data[DOMAIN][entry.entry_id]
    has_heating = coordinator.has_heating()

    entities = [
        FanOverrideBinarySensor(coordinator, entry),
        AlarmBinarySensor(coordinator, entry, "alarm_pressure_switch"),
        AlarmBinarySensor(coordinator, entry, "alarm_utility_lock"),
        AlarmBinarySensor(coordinator, entry, "alarm_door_open"),
        AlarmBinarySensor(coordinator, entry, "alarm_device_filter_dirty"),
        AlarmBinarySensor(coordinator, entry, "alarm_upstream_filter_dirty"),
        AlarmBinarySensor(coordinator, entry, "alarm_off_peak_disabled"),
        AlarmBinarySensor(coordinator, entry, "alarm_supply_voltage_off"),
        AlarmBinarySensor(coordinator, entry, "alarm_pressostat_triggered"),
        AlarmBinarySensor(coordinator, entry, "alarm_external_utility_lock"),
        AlarmBinarySensor(coordinator, entry, "alarm_emergency_mode"),
        AlarmBinarySensor(coordinator, entry, "alarm_supply_air_too_cold"),
    ]

    # Add heating-related binary sensors only for WGT devices
    if has_heating:
        entities.extend([
            NhrStateBinarySensor(coordinator, entry),
            Preheater1BinarySensor(coordinator, entry),
            Preheater2BinarySensor(coordinator, entry),
            AlarmBinarySensor(coordinator, entry, "alarm_heating_module_test", enabled_by_default=False),
            AlarmBinarySensor(coordinator, entry, "alarm_supply_air_cold"),
        ]
    )

    # Add room auxiliary heating active binary sensors (only for WGT devices)
    device_type = entry.data.get("device_type", "wgt")
    if device_type == "wgt":
        rooms = entry.data.get("rooms", [])
        for room in rooms:
            entities.append(
                RoomAuxiliaryHeatingActiveBinarySensor(coordinator, room["number"], room["name"])
            )

    async_add_entities(entities)


class FanOverrideBinarySensor(CoordinatorEntity[Coordinator], BinarySensorEntity):
    """Binary sensor for WRG fan override (Luftstufen Überschreibung)."""

    _attr_has_entity_name = True
    _attr_translation_key = "fan_override"

    def __init__(
        self,
        coordinator: Coordinator,
        entry: ConfigEntry,
    ) -> None:
        """Initialize the binary sensor."""
        super().__init__(coordinator)
        self._attr_unique_id = f"{entry.entry_id}_fan_override"
        model = MODEL_WGT if coordinator.has_heating() else MODEL_WRT
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, entry.entry_id)},
            name="Lüftung",
            manufacturer=MANUFACTURER,
            model=model,
        )

    @property
    def is_on(self) -> bool | None:
        """Return true if fan override is active."""
        value = self.coordinator.getData(REG_FAN_OVERRIDE)
        if value is not None:
            return value == FAN_OVERRIDE_ACTIVE
        return None


class NhrStateBinarySensor(CoordinatorEntity[Coordinator], BinarySensorEntity):
    """Binary sensor for WRG NHR state (NHR Zustand)."""

    _attr_has_entity_name = True
    _attr_translation_key = "nhr_state"
    _attr_entity_registry_enabled_default = False

    def __init__(
        self,
        coordinator: Coordinator,
        entry: ConfigEntry,
    ) -> None:
        """Initialize the binary sensor."""
        super().__init__(coordinator)
        self._attr_unique_id = f"{entry.entry_id}_nhr_state"
        model = MODEL_WGT if coordinator.has_heating() else MODEL_WRT
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, entry.entry_id)},
            name="Lüftung",
            manufacturer=MANUFACTURER,
            model=model,
        )

    @property
    def is_on(self) -> bool | None:
        """Return true if NHR is active."""
        return self.coordinator.getData(REG_NHR_STATE)


class Preheater1BinarySensor(CoordinatorEntity[Coordinator], BinarySensorEntity):
    """Binary sensor for WRG preheater 1 state (Vorheizregister 1)."""

    _attr_has_entity_name = True
    _attr_translation_key = "preheater_1"
    _attr_entity_registry_enabled_default = False

    def __init__(
        self,
        coordinator: Coordinator,
        entry: ConfigEntry,
    ) -> None:
        """Initialize the binary sensor."""
        super().__init__(coordinator)
        self._attr_unique_id = f"{entry.entry_id}_preheater_1"
        model = MODEL_WGT if coordinator.has_heating() else MODEL_WRT
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, entry.entry_id)},
            name="Lüftung",
            manufacturer=MANUFACTURER,
            model=model,
        )

    @property
    def is_on(self) -> bool | None:
        """Return true if preheater 1 (VHR 1) is active."""
        value = self.coordinator.data.get("preheater_state")
        if value is not None:
            return value in (PREHEATER_STATE_VHR1_ACTIVE, PREHEATER_STATE_VHR1_2_ACTIVE)
        return None


class Preheater2BinarySensor(CoordinatorEntity[Coordinator], BinarySensorEntity):
    """Binary sensor for WRG preheater 2 state (Vorheizregister 2)."""

    _attr_has_entity_name = True
    _attr_translation_key = "preheater_2"
    _attr_entity_registry_enabled_default = False

    def __init__(
        self,
        coordinator: Coordinator,
        entry: ConfigEntry,
    ) -> None:
        """Initialize the binary sensor."""
        super().__init__(coordinator)
        self._attr_unique_id = f"{entry.entry_id}_preheater_2"
        model = MODEL_WGT if coordinator.has_heating() else MODEL_WRT
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, entry.entry_id)},
            name="Lüftung",
            manufacturer=MANUFACTURER,
            model=model,
        )

    @property
    def is_on(self) -> bool | None:
        """Return true if preheater 2 (VHR 2) is active."""
        value = self.coordinator.data.get("preheater_state")
        if value is not None:
            return value in (PREHEATER_STATE_VHR2_ACTIVE, PREHEATER_STATE_VHR1_2_ACTIVE)
        return None


class AlarmBinarySensor(CoordinatorEntity[Coordinator], BinarySensorEntity):
    """Binary sensor for WRG alarms."""

    _attr_has_entity_name = True
    _attr_device_class = BinarySensorDeviceClass.PROBLEM

    def __init__(
        self,
        coordinator: Coordinator,
        entry: ConfigEntry,
        key: str,
        enabled_by_default: bool = True,
    ) -> None:
        """Initialize the binary sensor."""
        super().__init__(coordinator)
        self._key = key
        self._attr_translation_key = key
        self._attr_unique_id = f"{entry.entry_id}_{key}"
        self._attr_entity_registry_enabled_default = enabled_by_default
        model = MODEL_WGT if coordinator.has_heating() else MODEL_WRT
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, entry.entry_id)},
            name="Lüftung",
            manufacturer=MANUFACTURER,
            model=model,
        )

    @property
    def is_on(self) -> bool | None:
        """Return true if the binary sensor is on (alarm active)."""
        value = self.coordinator.data.get(self._key)
        if value is not None:
            return value == ALARM_ACTIVE
        return None


class RoomAuxiliaryHeatingActiveBinarySensor(
    CoordinatorEntity[Coordinator], BinarySensorEntity
):
    """Binary sensor for room auxiliary heating active status."""

    _attr_has_entity_name = True
    _attr_device_class = BinarySensorDeviceClass.HEAT

    def __init__(
        self,
        coordinator: Coordinator,
        room_number: int,
        room_name: str,
    ) -> None:
        """Initialize the binary sensor."""
        super().__init__(coordinator)
        self._room_number = room_number
        self._room_name = room_name
        self._attr_unique_id = f"{coordinator.config_entry.entry_id}_room_{room_number}_auxiliary_heating_active"
        self._attr_translation_key = "auxiliary_heating_active"

        # Room-specific device
        self._attr_device_info = {
            "identifiers": {(DOMAIN, f"{coordinator.config_entry.entry_id}_room_{room_number}")},
            "name": room_name,
            "manufacturer": MANUFACTURER,
            "model": "Room Climate Control",
            "via_device": (DOMAIN, coordinator.config_entry.entry_id),
        }

    @property
    def is_on(self) -> bool | None:
        """Return true if auxiliary heating is active."""
        # Register 460-476 for rooms 1-17
        return self.coordinator.getData(REG_HEATING_ACTIVE_1 + (self._room_number - 1))
