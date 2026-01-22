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
        FanOverrideBinarySensor(coordinator),
        AlarmBinarySensor(coordinator, REG_ALARM_PRESSURE_SWITCH),
        AlarmBinarySensor(coordinator, REG_ALARM_UTILITY_LOCK),
        AlarmBinarySensor(coordinator, REG_ALARM_DOOR_OPEN),
        AlarmBinarySensor(coordinator, REG_ALARM_DEVICE_FILTER_DIRTY),
        AlarmBinarySensor(coordinator, REG_ALARM_UPSTREAM_FILTER_DIRTY),
        AlarmBinarySensor(coordinator, REG_ALARM_OFF_PEAK_DISABLED),
        AlarmBinarySensor(coordinator, REG_ALARM_SUPPLY_VOLTAGE_OFF),
        AlarmBinarySensor(coordinator, REG_ALARM_PRESSOSTAT_TRIGGERED),
        AlarmBinarySensor(coordinator, REG_ALARM_EXTERNAL_UTILITY_LOCK),
        AlarmBinarySensor(coordinator, REG_ALARM_EMERGENCY_MODE),
    ])

    # Add heating-related binary sensors only for WGT devices
    if has_heating:
        entities.extend([
            NhrStateBinarySensor(coordinator),
            Preheater1BinarySensor(coordinator),
            Preheater2BinarySensor(coordinator),
            AlarmBinarySensor(coordinator, REG_ALARM_HEATING_MODULE_TEST, enabled_by_default=False),
            AlarmBinarySensor(coordinator, REG_ALARM_SUPPLY_AIR_COLD),
        ]
    )

    # Add room auxiliary heating active binary sensors ()
    device_type = entry.data.get("device_type", "wgt")
    if device_type == "wgt":
        rooms = entry.data.get("rooms", [])
        for room in rooms:
            entities.append(
                RoomAuxiliaryHeatingActiveBinarySensor(coordinator, room["number"])
            )

    async_add_entities(entities)


class FanOverrideBinarySensor(AbstractBinarySensor):
    def __init__(self, coordinator: Coordinator) -> None:
        super().__init__(coordinator, REG_FAN_OVERRIDE, {FAN_OVERRIDE_ACTIVE})

class NhrStateBinarySensor(AbstractBinarySensor):
    def __init__(self, coordinator: Coordinator) -> None:
        super().__init__(coordinator, REG_NHR_STATE)

class Preheater1BinarySensor(AbstractBinarySensor):
    def __init__(self, coordinator: Coordinator) -> None:
        super().__init__(
            coordinator, REG_PREHEATER_STATE, {PREHEATER_STATE_VHR1_ACTIVE, PREHEATER_STATE_VHR1_2_ACTIVE}
        )
        self._attr_entity_registry_enabled_default = False
        self._attr_translation_key = "preheater_1"
        self._attr_unique_id = f"{coordinator.config_entry.entry_id}_preheater_1"

class Preheater2BinarySensor(AbstractBinarySensor):
    def __init__(self, coordinator: Coordinator) -> None:
        super().__init__(
            coordinator, REG_PREHEATER_STATE, {PREHEATER_STATE_VHR2_ACTIVE, PREHEATER_STATE_VHR1_2_ACTIVE}
        )
        self._attr_entity_registry_enabled_default = False
        self._attr_translation_key = "preheater_2"
        self._attr_unique_id = f"{coordinator.config_entry.entry_id}_preheater_2"

class AlarmBinarySensor(AbstractBinarySensor):
    _attr_device_class = BinarySensorDeviceClass.PROBLEM

    def __init__(
        self,
        coordinator: Coordinator,
        register: int,
        enabled_by_default: bool = True,
    ) -> None:
        super().__init__(coordinator, register, {ALARM_ACTIVE})

        self._attr_entity_registry_enabled_default = enabled_by_default

class RoomAuxiliaryHeatingActiveBinarySensor(AbstarctBinaryRoomSensor):
    _attr_device_class = BinarySensorDeviceClass.HEAT

    def __init__(
        self,
        coordinator: Coordinator,
        room_number: int,
    ) -> None:
        super().__init__(coordinator, room_number, REG_HEATING_ACTIVE_1, None)
        self._attr_translation_key = "auxiliary_heating_active"

