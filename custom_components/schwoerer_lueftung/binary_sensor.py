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

from custom_components.schwoerer_lueftung.abstract import (AbstractBinarySensor, AbstarctBinaryRoomSensor)

from .const import DOMAIN, MANUFACTURER, MODEL_WGT, MODEL_WRT
from .coordinator import Coordinator
from .modbus.registers import (
    ALARM_ACTIVE,
    FAN_OVERRIDE_ACTIVE,
    PREHEATER_STATE_VHR1_2_ACTIVE,
    PREHEATER_STATE_VHR1_ACTIVE,
    PREHEATER_STATE_VHR2_ACTIVE,
    REG_ALARM_DEVICE_FILTER_DIRTY,
    REG_ALARM_DOOR_OPEN,
    REG_ALARM_EMERGENCY_MODE,
    REG_ALARM_EXTERNAL_UTILITY_LOCK,
    REG_ALARM_HEATING_MODULE_TEST,
    REG_ALARM_OFF_PEAK_DISABLED,
    REG_ALARM_PRESSOSTAT_TRIGGERED,
    REG_ALARM_PRESSURE_SWITCH,
    REG_ALARM_SUPPLY_AIR_COLD,
    REG_ALARM_SUPPLY_VOLTAGE_OFF,
    REG_ALARM_UPSTREAM_FILTER_DIRTY,
    REG_ALARM_UTILITY_LOCK,
    REG_FAN_OVERRIDE,
    REG_HEATING_ACTIVE_1,
    REG_NHR_STATE,
    REG_PREHEATER_STATE,
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

    model = MODEL_WGT if coordinator.has_heating() else MODEL_WRT
    device = DeviceInfo(
        identifiers={(DOMAIN, entry.entry_id)},
        name="Lüftung",
        manufacturer=MANUFACTURER,
        model=model,
    )


    entities = []
    entities.extend([
        FanOverrideBinarySensor(coordinator, device),
        AlarmBinarySensor(coordinator, device, REG_ALARM_PRESSURE_SWITCH),
        AlarmBinarySensor(coordinator, device, REG_ALARM_UTILITY_LOCK),
        AlarmBinarySensor(coordinator, device, REG_ALARM_DOOR_OPEN),
        AlarmBinarySensor(coordinator, device, REG_ALARM_DEVICE_FILTER_DIRTY),
        AlarmBinarySensor(coordinator, device, REG_ALARM_UPSTREAM_FILTER_DIRTY),
        AlarmBinarySensor(coordinator, device, REG_ALARM_OFF_PEAK_DISABLED),
        AlarmBinarySensor(coordinator, device, REG_ALARM_SUPPLY_VOLTAGE_OFF),
        AlarmBinarySensor(coordinator, device, REG_ALARM_PRESSOSTAT_TRIGGERED),
        AlarmBinarySensor(coordinator, device, REG_ALARM_EXTERNAL_UTILITY_LOCK),
        AlarmBinarySensor(coordinator, device, REG_ALARM_EMERGENCY_MODE),
    ])

    # Add heating-related binary sensors only for WGT devices
    if has_heating:
        entities.extend([
            NhrStateBinarySensor(coordinator, device),
            Preheater1BinarySensor(coordinator, device),
            Preheater2BinarySensor(coordinator, device),
            AlarmBinarySensor(coordinator, device, REG_ALARM_HEATING_MODULE_TEST, enabled_by_default=False),
            AlarmBinarySensor(coordinator, device, REG_ALARM_SUPPLY_AIR_COLD),
        ]
    )

    # Add room auxiliary heating active binary sensors (only for WGT devices)
    device_type = entry.data.get("device_type", "wgt")
    if device_type == "wgt":
        rooms = entry.data.get("rooms", [])
        for room in rooms:
            room_device = DeviceInfo(
                identifiers={
                    (DOMAIN, f"{coordinator.config_entry.entry_id}_room_{room["number"]}")
                },
                name=room["name"],
                manufacturer=MANUFACTURER,
                model="Room Climate Control",
                via_device=(DOMAIN, coordinator.config_entry.entry_id),
            )
            entities.append(
                RoomAuxiliaryHeatingActiveBinarySensor(coordinator, room_device, room["number"])
            )

    async_add_entities(entities)


class FanOverrideBinarySensor(AbstractBinarySensor):
    def __init__(self, coordinator: Coordinator, device: DeviceInfo) -> None:
        super().__init__(coordinator, device, REG_FAN_OVERRIDE, {FAN_OVERRIDE_ACTIVE})

class NhrStateBinarySensor(AbstractBinarySensor):
    def __init__(self, coordinator: Coordinator, device: DeviceInfo) -> None:
        super().__init__(coordinator, device, REG_NHR_STATE)

class Preheater1BinarySensor(AbstractBinarySensor):
    def __init__(self, coordinator: Coordinator, device: DeviceInfo) -> None:
        super().__init__(
            coordinator, device, REG_PREHEATER_STATE, {PREHEATER_STATE_VHR1_ACTIVE, PREHEATER_STATE_VHR1_2_ACTIVE}
        )
        self._attr_entity_registry_enabled_default = False
        self._attr_translation_key = "preheater_1"
        self._attr_unique_id = f"{coordinator.config_entry.entry_id}_preheater_1"

class Preheater2BinarySensor(AbstractBinarySensor):
    def __init__(self, coordinator: Coordinator, device: DeviceInfo) -> None:
        super().__init__(
            coordinator, device, REG_PREHEATER_STATE, {PREHEATER_STATE_VHR2_ACTIVE, PREHEATER_STATE_VHR1_2_ACTIVE}
        )
        self._attr_entity_registry_enabled_default = False
        self._attr_translation_key = "preheater_2"
        self._attr_unique_id = f"{coordinator.config_entry.entry_id}_preheater_2"

class AlarmBinarySensor(AbstractBinarySensor):
    _attr_device_class = BinarySensorDeviceClass.PROBLEM

    def __init__(
        self,
        coordinator: Coordinator,
        device: DeviceInfo,
        register: int,
        enabled_by_default: bool = True,
    ) -> None:
        super().__init__(coordinator, device, register, {ALARM_ACTIVE})

        self._attr_entity_registry_enabled_default = enabled_by_default

class RoomAuxiliaryHeatingActiveBinarySensor(AbstarctBinaryRoomSensor):
    _attr_device_class = BinarySensorDeviceClass.HEAT

    def __init__(
        self,
        coordinator: Coordinator,
        device: DeviceInfo,
        room_number: int,
    ) -> None:
        super().__init__(coordinator, device, room_number, REG_HEATING_ACTIVE_1, None)
        self._attr_translation_key = "auxiliary_heating_active"

