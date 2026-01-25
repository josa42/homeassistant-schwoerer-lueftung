from __future__ import annotations

from homeassistant.components.binary_sensor import (
    BinarySensorDeviceClass,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .abstract import AbstarctBinaryRoomSensor, AbstractBinarySensor
from .const import DOMAIN
from .coordinator import Coordinator
from .modbus.registers import (
    ALARM_ACTIVE,
    FAN_OVERRIDE_ACTIVE,
    PREHEATER_STATE_PREHEATING_COIL_1_2_ACTIVE,
    PREHEATER_STATE_PREHEATING_COIL_1_ACTIVE,
    PREHEATER_STATE_PREHEATING_COIL_2_ACTIVE,
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
    REG_AUXILIARY_HEATING_ACTIVE_ROOM_1,
    REG_AUXILIARY_HEATING_ENABLED_ROOM_1,
    REG_FAN_OVERRIDE,
    REG_REHEATER_STATE,
    REG_OUTDOOR_DAMPER_STATE,
    REG_PREHEATER_STATE,
)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up WRG binary sensors from a config entry."""
    coordinator: Coordinator = hass.data[DOMAIN][entry.entry_id]
    has_heating = coordinator.has_heating()

    entities = []
    entities.extend([
        FanOverrideBinarySensor(coordinator),
        AlarmBinarySensor(coordinator, REG_ALARM_PRESSURE_SWITCH, enabled_by_default=False),
        AlarmBinarySensor(coordinator, REG_ALARM_UTILITY_LOCK, enabled_by_default=False),
        AlarmBinarySensor(coordinator, REG_ALARM_DOOR_OPEN),
        AlarmBinarySensor(coordinator, REG_ALARM_DEVICE_FILTER_DIRTY),
        AlarmBinarySensor(coordinator, REG_ALARM_UPSTREAM_FILTER_DIRTY),
        AlarmBinarySensor(coordinator, REG_ALARM_OFF_PEAK_DISABLED, enabled_by_default=False),
        AlarmBinarySensor(coordinator, REG_ALARM_SUPPLY_VOLTAGE_OFF, enabled_by_default=False),
        AlarmBinarySensor(coordinator, REG_ALARM_PRESSOSTAT_TRIGGERED, enabled_by_default=False),
        AlarmBinarySensor(coordinator, REG_ALARM_EXTERNAL_UTILITY_LOCK, enabled_by_default=False),
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
        ])

        for room in entry.data.get("rooms", []):
            entities.extend([
                RoomAuxiliaryHeatingEnabledSensor(coordinator, room["number"]),
                RoomAuxiliaryHeatingActiveBinarySensor(coordinator, room["number"])
            ])

    async_add_entities(entities)

class OutdoorDamperStateSensor(AbstractBinarySensor):
    """
    Outdoor Damper State Binary Sensor
    (Aussenklappe Zustand)

    Register: 131
    Values:     0 = Closed
                1 = Open
    """
    def __init__(self, coordinator: Coordinator) -> None:
        super().__init__(coordinator, REG_OUTDOOR_DAMPER_STATE)

class FanOverrideBinarySensor(AbstractBinarySensor):
    """
    Fan Override Binary Sensor
    (Luftstufen Überschreibung)

    Register: 104
    Values:     0 = Inactive
                1 = Active
    """
    def __init__(self, coordinator: Coordinator) -> None:
        super().__init__(coordinator, REG_FAN_OVERRIDE, {FAN_OVERRIDE_ACTIVE})

class NhrStateBinarySensor(AbstractBinarySensor):
    def __init__(self, coordinator: Coordinator) -> None:
        super().__init__(coordinator, REG_REHEATER_STATE)
        self._attr_entity_registry_enabled_default = False

class Preheater1BinarySensor(AbstractBinarySensor):
    def __init__(self, coordinator: Coordinator) -> None:
        super().__init__(
            coordinator,
            REG_PREHEATER_STATE,
            {
                PREHEATER_STATE_PREHEATING_COIL_1_ACTIVE,
                PREHEATER_STATE_PREHEATING_COIL_1_2_ACTIVE,
            },
            key="preheater_",
            enabled_by_default=False,
        )

class Preheater2BinarySensor(AbstractBinarySensor):
    def __init__(self, coordinator: Coordinator) -> None:
        super().__init__(
            coordinator,
            REG_PREHEATER_STATE,
            {
                PREHEATER_STATE_PREHEATING_COIL_2_ACTIVE,
                PREHEATER_STATE_PREHEATING_COIL_1_2_ACTIVE,
            },
            key="preheater_2",
            enabled_by_default=False,
        )

class AlarmBinarySensor(AbstractBinarySensor):
    def __init__(
        self,
        coordinator: Coordinator,
        register: int,
        enabled_by_default: bool = True,
    ) -> None:
        super().__init__(
            coordinator,
            register,
            {ALARM_ACTIVE},
            enabled_by_default=enabled_by_default,
            device_class=BinarySensorDeviceClass.PROBLEM,
        )

class RoomAuxiliaryHeatingEnabledSensor(AbstarctBinaryRoomSensor):
    """
    Room Auxiliary Heating Enabled Sensor
    (Zusatzheizung Freigabe Raum 1-17)

    Register: 440-456
    Values:     0 = Blocked
                1 = Heating Enabled
    """
    def __init__(self, coordinator: Coordinator, room_number: int) -> None:
        super().__init__(
            coordinator,
            REG_AUXILIARY_HEATING_ENABLED_ROOM_1,
            room_number,
            enabled_by_default=True
        )

class RoomAuxiliaryHeatingActiveBinarySensor(AbstarctBinaryRoomSensor):
    def __init__(
        self,
        coordinator: Coordinator,
        room_number: int,
    ) -> None:
        super().__init__(
            coordinator,
            REG_AUXILIARY_HEATING_ACTIVE_ROOM_1,
            room_number,
            device_class=BinarySensorDeviceClass.HEAT
        )
