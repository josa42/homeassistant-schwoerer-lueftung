"""Switch platform for BIC WRG."""
from __future__ import annotations

import logging
from typing import Any

from homeassistant.components.switch import SwitchEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN, MANUFACTURER, MODEL_WGT, MODEL_WRT
from .coordinator import Coordinator
from .modbus_client import (
    AUXILIARY_HEATING_ENABLED,
    AUXILIARY_HEATING_OFF,
    HEAT_PUMP_COOLING_ENABLED,
    HEAT_PUMP_COOLING_OFF,
    HEAT_PUMP_HEATING_ENABLED,
    HEAT_PUMP_HEATING_OFF,
    REG_HEATING_ENABLED_1,
    REG_SCHECHULD_HEATING_ENABLED_1,
    SHOCK_VENTILATION_ACTIVE,
    SHOCK_VENTILATION_INACTIVE,
)

_LOGGER = logging.getLogger(__name__)

async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up WRG switch entities from a config entry."""
    coordinator: Coordinator = hass.data[DOMAIN][entry.entry_id]
    has_heating = coordinator.has_heating()

    entities = []
    entities.extend([
        ShockVentilationSwitch(coordinator, entry),
    ])

    # Add heating-related switches only for WGT devices
    if has_heating:
        entities.extend([
            HeatPumpHeatingSwitch(coordinator, entry),
            HeatPumpCoolingSwitch(coordinator, entry),
            AuxiliaryHeatingSwitch(coordinator, entry),
        ])

    # Add room heating switches (only for WGT)
    if has_heating:
        rooms = entry.data.get("rooms", [])
        for room in rooms:
            entities.append(
                RoomAuxiliaryHeatingEnableSwitch(
                    coordinator, room["number"], room["name"]
                )
            )
            entities.append(
                RoomTimeProgramHeatingEnableSwitch(
                    coordinator, room["number"], room["name"]
                )
            )

    async_add_entities(entities)


class ShockVentilationSwitch(CoordinatorEntity[Coordinator], SwitchEntity):
    """Switch entity for WRG shock ventilation (Stoßlüftung)."""

    _attr_has_entity_name = True
    _attr_translation_key = "shock_ventilation"

    def __init__(
        self,
        coordinator: Coordinator,
        entry: ConfigEntry,
    ) -> None:
        """Initialize the switch entity."""
        super().__init__(coordinator)
        self._attr_unique_id = f"{entry.entry_id}_shock_ventilation"
        model = MODEL_WGT if coordinator.has_heating() else MODEL_WRT
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, entry.entry_id)},
            name="Lüftung",
            manufacturer=MANUFACTURER,
            model=model,
        )

    @property
    def is_on(self) -> bool | None:
        """Return true if shock ventilation is active."""
        value = self.coordinator.data.get("shock_ventilation")
        if value is not None:
            return value == SHOCK_VENTILATION_ACTIVE
        return None

    async def async_turn_on(self, **kwargs: Any) -> None:
        """Turn on shock ventilation."""
        success = await self.hass.async_add_executor_job(
            self.coordinator.client.write_shock_ventilation, SHOCK_VENTILATION_ACTIVE
        )

        if success:
            await self.coordinator.async_request_refresh()

    async def async_turn_off(self, **kwargs: Any) -> None:
        """Turn off shock ventilation."""
        success = await self.hass.async_add_executor_job(
            self.coordinator.client.write_shock_ventilation, SHOCK_VENTILATION_INACTIVE
        )

        if success:
            await self.coordinator.async_request_refresh()


class RoomAuxiliaryHeatingEnableSwitch(CoordinatorEntity[Coordinator], SwitchEntity):
    """Switch entity for room auxiliary heating enable (Zusatzheizung Freigabe)."""

    _attr_has_entity_name = True
    _attr_entity_registry_enabled_default = False

    def __init__(
        self,
        coordinator: Coordinator,
        room_number: int,
        room_name: str,
    ) -> None:
        """Initialize the switch entity."""
        super().__init__(coordinator)
        self._room_number = room_number
        self._room_name = room_name
        entry_id = coordinator.config_entry.entry_id
        self._attr_unique_id = (
            f"{entry_id}_room_{room_number}_auxiliary_heating_enable"
        )
        self._attr_translation_key = "auxiliary_heating_enable"

        # Room-specific device
        self._attr_device_info = {
            "identifiers": {(DOMAIN, f"{entry_id}_room_{room_number}")},
            "name": room_name,
            "manufacturer": MANUFACTURER,
            "model": "Room Climate Control",
            "via_device": (DOMAIN, coordinator.config_entry.entry_id),
        }

    @property
    def is_on(self) -> bool | None:
        """Return true if auxiliary heating is enabled."""
        # Register 440-456 for rooms 1-17
        value = self.coordinator.getData(REG_HEATING_ENABLED_1 + (self._room_number - 1))
        if value is not None:
            return value == 1
        return None

    async def async_turn_on(self, **kwargs: Any) -> None:
        """Enable auxiliary heating."""
        register = 440 + self._room_number - 1
        success = await self.hass.async_add_executor_job(
            self.coordinator.client.write_register, register, 1
        )

        if success:
            await self.coordinator.async_request_refresh()

    async def async_turn_off(self, **kwargs: Any) -> None:
        """Disable auxiliary heating."""
        register = 440 + self._room_number - 1
        success = await self.hass.async_add_executor_job(
            self.coordinator.client.write_register, register, 0
        )

        if success:
            await self.coordinator.async_request_refresh()


class RoomTimeProgramHeatingEnableSwitch(CoordinatorEntity[Coordinator], SwitchEntity):
    """Switch entity for room time program heating enable.

    Freigabe Zeitprogramm Heizen.
    """

    _attr_has_entity_name = True
    _attr_entity_registry_enabled_default = False

    def __init__(
        self,
        coordinator: Coordinator,
        room_number: int,
        room_name: str,
    ) -> None:
        """Initialize the switch entity."""
        super().__init__(coordinator)
        self._room_number = room_number
        self._room_name = room_name
        entry_id = coordinator.config_entry.entry_id
        self._attr_unique_id = (
            f"{entry_id}_room_{room_number}_scheduled_heating_enable"
        )
        self._attr_translation_key = "scheduled_heating_enable"

        # Room-specific device
        self._attr_device_info = {
            "identifiers": {(DOMAIN, f"{entry_id}_room_{room_number}")},
            "name": room_name,
            "manufacturer": MANUFACTURER,
            "model": "Room Climate Control",
            "via_device": (DOMAIN, coordinator.config_entry.entry_id),
        }

    @property
    def is_on(self) -> bool | None:
        """Return true if time program heating is enabled."""
        # Register 500-516 for rooms 1-17
        return self.coordinator.getData(REG_SCHECHULD_HEATING_ENABLED_1 + (self._room_number - 1))

    async def async_turn_on(self, **kwargs: Any) -> None:
        """Enable time program heating."""
        register = 500 + self._room_number - 1
        success = await self.hass.async_add_executor_job(
            self.coordinator.client.write_register, register, 1
        )

        if success:
            await self.coordinator.async_request_refresh()

    async def async_turn_off(self, **kwargs: Any) -> None:
        """Disable time program heating."""
        register = 500 + self._room_number - 1
        success = await self.hass.async_add_executor_job(
            self.coordinator.client.write_register, register, 0
        )

        if success:
            await self.coordinator.async_request_refresh()


class HeatPumpHeatingSwitch(CoordinatorEntity[Coordinator], SwitchEntity):
    """Switch entity for WRG heat pump heating (Wärmepumpe Heizen)."""

    _attr_has_entity_name = True
    _attr_translation_key = "heat_pump_heating"

    def __init__(
        self,
        coordinator: Coordinator,
        entry: ConfigEntry,
    ) -> None:
        """Initialize the switch entity."""
        super().__init__(coordinator)
        self._attr_unique_id = f"{entry.entry_id}_heat_pump_heating_enable"
        model = MODEL_WGT if coordinator.has_heating() else MODEL_WRT
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, entry.entry_id)},
            name="Lüftung",
            manufacturer=MANUFACTURER,
            model=model,
        )

    @property
    def is_on(self) -> bool | None:
        """Return true if heat pump heating is enabled."""
        value = self.coordinator.data.get("heat_pump_heating_enable")
        if value is not None:
            return value == HEAT_PUMP_HEATING_ENABLED
        return None

    async def async_turn_on(self, **kwargs: Any) -> None:
        """Enable heat pump heating."""
        success = await self.hass.async_add_executor_job(
            self.coordinator.client.write_heat_pump_heating_enable,
            HEAT_PUMP_HEATING_ENABLED,
        )

        if success:
            await self.coordinator.async_request_refresh()

    async def async_turn_off(self, **kwargs: Any) -> None:
        """Disable heat pump heating."""
        success = await self.hass.async_add_executor_job(
            self.coordinator.client.write_heat_pump_heating_enable,
            HEAT_PUMP_HEATING_OFF,
        )

        if success:
            await self.coordinator.async_request_refresh()


class HeatPumpCoolingSwitch(CoordinatorEntity[Coordinator], SwitchEntity):
    """Switch entity for WRG heat pump cooling (Wärmepumpe Kühlen)."""

    _attr_has_entity_name = True
    _attr_translation_key = "heat_pump_cooling"

    def __init__(
        self,
        coordinator: Coordinator,
        entry: ConfigEntry,
    ) -> None:
        """Initialize the switch entity."""
        super().__init__(coordinator)
        self._attr_unique_id = f"{entry.entry_id}_heat_pump_cooling_enable"
        model = MODEL_WGT if coordinator.has_heating() else MODEL_WRT
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, entry.entry_id)},
            name="Lüftung",
            manufacturer=MANUFACTURER,
            model=model,
        )

    @property
    def is_on(self) -> bool | None:
        """Return true if heat pump cooling is enabled."""
        value = self.coordinator.data.get("heat_pump_cooling_enable")
        if value is not None:
            return value == HEAT_PUMP_COOLING_ENABLED
        return None

    async def async_turn_on(self, **kwargs: Any) -> None:
        """Enable heat pump cooling."""
        success = await self.hass.async_add_executor_job(
            self.coordinator.client.write_heat_pump_cooling_enable,
            HEAT_PUMP_COOLING_ENABLED,
        )

        if success:
            await self.coordinator.async_request_refresh()

    async def async_turn_off(self, **kwargs: Any) -> None:
        """Disable heat pump cooling."""
        success = await self.hass.async_add_executor_job(
            self.coordinator.client.write_heat_pump_cooling_enable,
            HEAT_PUMP_COOLING_OFF,
        )

        if success:
            await self.coordinator.async_request_refresh()


class AuxiliaryHeatingSwitch(CoordinatorEntity[Coordinator], SwitchEntity):
    """Switch entity for WRG auxiliary house heating (Zusatzheizung Haus)."""

    _attr_has_entity_name = True
    _attr_translation_key = "auxiliary_house_heating"

    def __init__(
        self,
        coordinator: Coordinator,
        entry: ConfigEntry,
    ) -> None:
        """Initialize the switch entity."""
        super().__init__(coordinator)
        self._attr_unique_id = f"{entry.entry_id}_auxiliary_heating_enable"
        model = MODEL_WGT if coordinator.has_heating() else MODEL_WRT
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, entry.entry_id)},
            name="Lüftung",
            manufacturer=MANUFACTURER,
            model=model,
        )

    @property
    def is_on(self) -> bool | None:
        """Return true if auxiliary house heating is enabled."""
        value = self.coordinator.data.get("auxiliary_heating_enable")
        if value is not None:
            return value == AUXILIARY_HEATING_ENABLED
        return None

    async def async_turn_on(self, **kwargs: Any) -> None:
        """Enable auxiliary house heating."""
        success = await self.hass.async_add_executor_job(
            self.coordinator.client.write_auxiliary_heating_enable,
            AUXILIARY_HEATING_ENABLED,
        )

        if success:
            await self.coordinator.async_request_refresh()

    async def async_turn_off(self, **kwargs: Any) -> None:
        """Disable auxiliary house heating."""
        success = await self.hass.async_add_executor_job(
            self.coordinator.client.write_auxiliary_heating_enable,
            AUXILIARY_HEATING_OFF,
        )

        if success:
            await self.coordinator.async_request_refresh()
