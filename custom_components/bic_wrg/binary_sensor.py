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
from .modbus_client import (
    ALARM_ACTIVE,
    FAN_OVERRIDE_ACTIVE,
    NHR_STATE_ACTIVE,
    PREHEATER_STATE_VHR1_ACTIVE,
    PREHEATER_STATE_VHR2_ACTIVE,
    PREHEATER_STATE_VHR1_2_ACTIVE,
)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up WRG binary sensors from a config entry."""
    coordinator: BicWrgCoordinator = hass.data[DOMAIN][entry.entry_id]
    
    entities = [
        BicWrgFanOverrideBinarySensor(coordinator, entry),
        BicWrgNhrStateBinarySensor(coordinator, entry),
        BicWrgPreheater1BinarySensor(coordinator, entry),
        BicWrgPreheater2BinarySensor(coordinator, entry),
        BicWrgAlarmBinarySensor(
            coordinator, entry, "alarm_pressure_switch", "alarm_pressure_switch"
        ),
        BicWrgAlarmBinarySensor(
            coordinator, entry, "alarm_utility_lock", "alarm_utility_lock"
        ),
        BicWrgAlarmBinarySensor(
            coordinator, entry, "alarm_door_open", "alarm_door_open"
        ),
        BicWrgAlarmBinarySensor(
            coordinator, entry, "alarm_device_filter_dirty", "alarm_device_filter_dirty"
        ),
        BicWrgAlarmBinarySensor(
            coordinator, entry, "alarm_upstream_filter_dirty", "alarm_upstream_filter_dirty"
        ),
        BicWrgAlarmBinarySensor(
            coordinator, entry, "alarm_off_peak_disabled", "alarm_off_peak_disabled"
        ),
        BicWrgAlarmBinarySensor(
            coordinator, entry, "alarm_supply_voltage_off", "alarm_supply_voltage_off"
        ),
        BicWrgAlarmBinarySensor(
            coordinator, entry, "alarm_pressostat_triggered", "alarm_pressostat_triggered"
        ),
        BicWrgAlarmBinarySensor(
            coordinator, entry, "alarm_external_utility_lock", "alarm_external_utility_lock"
        ),
        BicWrgAlarmBinarySensor(
            coordinator, entry, "alarm_heating_module_test", "alarm_heating_module_test", enabled_by_default=False
        ),
        BicWrgAlarmBinarySensor(
            coordinator, entry, "alarm_emergency_mode", "alarm_emergency_mode"
        ),
        BicWrgAlarmBinarySensor(
            coordinator, entry, "alarm_supply_air_cold", "alarm_supply_air_cold"
        ),
    ]
    
    # Add room auxiliary heating active binary sensors
    rooms = entry.data.get("rooms", [])
    for room in rooms:
        entities.append(
            BicWrgRoomAuxiliaryHeatingActiveBinarySensor(coordinator, room["number"], room["name"])
        )
    
    async_add_entities(entities)


class BicWrgFanOverrideBinarySensor(CoordinatorEntity[BicWrgCoordinator], BinarySensorEntity):
    """Binary sensor for WRG fan override (Luftstufen Überschreibung)."""

    _attr_has_entity_name = True
    _attr_translation_key = "fan_override"

    def __init__(
        self,
        coordinator: BicWrgCoordinator,
        entry: ConfigEntry,
    ) -> None:
        """Initialize the binary sensor."""
        super().__init__(coordinator)
        self._attr_unique_id = f"{entry.entry_id}_fan_override"
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, entry.entry_id)},
            name="WRG 134-BP-HK",
            manufacturer=MANUFACTURER,
            model=MODEL,
        )

    @property
    def is_on(self) -> bool | None:
        """Return true if fan override is active."""
        value = self.coordinator.data.get("fan_override")
        if value is not None:
            return value == FAN_OVERRIDE_ACTIVE
        return None


class BicWrgNhrStateBinarySensor(CoordinatorEntity[BicWrgCoordinator], BinarySensorEntity):
    """Binary sensor for WRG NHR state (NHR Zustand)."""

    _attr_has_entity_name = True
    _attr_translation_key = "nhr_state"
    _attr_entity_registry_enabled_default = False

    def __init__(
        self,
        coordinator: BicWrgCoordinator,
        entry: ConfigEntry,
    ) -> None:
        """Initialize the binary sensor."""
        super().__init__(coordinator)
        self._attr_unique_id = f"{entry.entry_id}_nhr_state"
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, entry.entry_id)},
            name="WRG 134-BP-HK",
            manufacturer=MANUFACTURER,
            model=MODEL,
        )

    @property
    def is_on(self) -> bool | None:
        """Return true if NHR is active."""
        value = self.coordinator.data.get("nhr_state")
        if value is not None:
            return value == NHR_STATE_ACTIVE
        return None


class BicWrgPreheater1BinarySensor(CoordinatorEntity[BicWrgCoordinator], BinarySensorEntity):
    """Binary sensor for WRG preheater 1 state (Vorheizregister 1)."""

    _attr_has_entity_name = True
    _attr_translation_key = "preheater_1"
    _attr_entity_registry_enabled_default = False

    def __init__(
        self,
        coordinator: BicWrgCoordinator,
        entry: ConfigEntry,
    ) -> None:
        """Initialize the binary sensor."""
        super().__init__(coordinator)
        self._attr_unique_id = f"{entry.entry_id}_preheater_1"
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, entry.entry_id)},
            name="WRG 134-BP-HK",
            manufacturer=MANUFACTURER,
            model=MODEL,
        )

    @property
    def is_on(self) -> bool | None:
        """Return true if preheater 1 (VHR 1) is active."""
        value = self.coordinator.data.get("preheater_state")
        if value is not None:
            return value in (PREHEATER_STATE_VHR1_ACTIVE, PREHEATER_STATE_VHR1_2_ACTIVE)
        return None


class BicWrgPreheater2BinarySensor(CoordinatorEntity[BicWrgCoordinator], BinarySensorEntity):
    """Binary sensor for WRG preheater 2 state (Vorheizregister 2)."""

    _attr_has_entity_name = True
    _attr_translation_key = "preheater_2"
    _attr_entity_registry_enabled_default = False

    def __init__(
        self,
        coordinator: BicWrgCoordinator,
        entry: ConfigEntry,
    ) -> None:
        """Initialize the binary sensor."""
        super().__init__(coordinator)
        self._attr_unique_id = f"{entry.entry_id}_preheater_2"
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, entry.entry_id)},
            name="WRG 134-BP-HK",
            manufacturer=MANUFACTURER,
            model=MODEL,
        )

    @property
    def is_on(self) -> bool | None:
        """Return true if preheater 2 (VHR 2) is active."""
        value = self.coordinator.data.get("preheater_state")
        if value is not None:
            return value in (PREHEATER_STATE_VHR2_ACTIVE, PREHEATER_STATE_VHR1_2_ACTIVE)
        return None


class BicWrgAlarmBinarySensor(CoordinatorEntity[BicWrgCoordinator], BinarySensorEntity):
    """Binary sensor for WRG alarms."""

    _attr_has_entity_name = True
    _attr_device_class = BinarySensorDeviceClass.PROBLEM

    def __init__(
        self,
        coordinator: BicWrgCoordinator,
        entry: ConfigEntry,
        key: str,
        translation_key: str,
        enabled_by_default: bool = True,
    ) -> None:
        """Initialize the binary sensor."""
        super().__init__(coordinator)
        self._key = key
        self._attr_translation_key = translation_key
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


class BicWrgRoomAuxiliaryHeatingActiveBinarySensor(
    CoordinatorEntity[BicWrgCoordinator], BinarySensorEntity
):
    """Binary sensor for room auxiliary heating active status."""

    _attr_has_entity_name = True
    _attr_device_class = BinarySensorDeviceClass.HEAT

    def __init__(
        self,
        coordinator: BicWrgCoordinator,
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
        register = 460 + self._room_number - 1
        value = self.coordinator.data.get(f"register_{register}")
        if value is not None:
            return value == 1
        return None
