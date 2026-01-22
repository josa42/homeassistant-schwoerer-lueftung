"""Number platform for BIC WRG."""
from __future__ import annotations

from homeassistant.components.number import NumberEntity, NumberMode
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN, MANUFACTURER, MODEL_WGT, MODEL_WRT
from .coordinator import Coordinator
from .modbus.registers import (
    LINEAR_FAN_POWER_MAX,
    LINEAR_FAN_POWER_MIN,
    REG_BASE_TEMPERATURE_1,
    REG_LINEAR_FAN_POWER,
)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up WRG number entities from a config entry."""
    coordinator: Coordinator = hass.data[DOMAIN][entry.entry_id]

    entities = []
    entities.append(LinearFanPowerNumber(coordinator, entry))

    # Add base temperature numbers for each configured room (WGT only)
    if coordinator.has_heating():
        rooms = entry.data.get("rooms", [])
        for room in rooms:
            entities.append(
                RoomBaseTemperatureNumber(coordinator, entry, room["number"], room["name"])
            )

    async_add_entities(entities)


class LinearFanPowerNumber(CoordinatorEntity[Coordinator], NumberEntity):
    """Number entity for WRG linear fan power (Manuelle Lineare Luftleistung)."""

    _attr_has_entity_name = True
    _attr_translation_key = "linear_fan_power"
    _attr_native_min_value = LINEAR_FAN_POWER_MIN
    _attr_native_max_value = LINEAR_FAN_POWER_MAX
    _attr_native_step = 1
    _attr_native_unit_of_measurement = "%"
    _attr_mode = NumberMode.SLIDER
    _attr_entity_registry_enabled_default = False

    def __init__(
        self,
        coordinator: Coordinator,
        entry: ConfigEntry,
    ) -> None:
        """Initialize the number entity."""
        super().__init__(coordinator)
        self._attr_unique_id = f"{entry.entry_id}_linear_fan_power"
        model = MODEL_WGT if coordinator.has_heating() else MODEL_WRT
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, entry.entry_id)},
            name="Lüftung",
            manufacturer=MANUFACTURER,
            model=model,
        )

    @property
    def native_value(self) -> float | None:
        """Return the current linear fan power."""
        return self.coordinator.getData(REG_LINEAR_FAN_POWER)

    async def async_set_native_value(self, value: float) -> None:
        """Set the linear fan power."""
        # Write to device
        success = await self.hass.async_add_executor_job(
            self.coordinator.client.write_linear_fan_power, int(value)
        )

        if success:
            # Update coordinator data immediately
            await self.coordinator.async_request_refresh()


class RoomBaseTemperatureNumber(CoordinatorEntity[Coordinator], NumberEntity):
    """Number entity for room base temperature (Grundtemperatur)."""

    _attr_has_entity_name = True
    _attr_native_min_value = 10.0
    _attr_native_max_value = 30.0
    _attr_native_step = 0.1
    _attr_native_unit_of_measurement = "°C"
    _attr_mode = NumberMode.BOX
    _attr_entity_registry_enabled_default = False

    def __init__(
        self,
        coordinator: Coordinator,
        entry: ConfigEntry,
        room_number: int,
        room_name: str,
    ) -> None:
        """Initialize the number entity."""
        super().__init__(coordinator)

        # Validate room number (1-17 as per Modbus documentation)
        if not 1 <= room_number <= 17:
            raise ValueError(f"Room number must be between 1 and 17, got {room_number}")

        self._room_number = room_number
        self._room_name = room_name
        self._attr_translation_key = "base_temperature"
        self._attr_unique_id = f"{entry.entry_id}_base_tempemerature_{room_number}"

        # Use same model as climate entity for consistency
        model = MODEL_WGT if coordinator.has_heating() else MODEL_WRT

        coordinator.client.subscribe(REG_BASE_TEMPERATURE_1 + (room_number - 1))

        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, f"{entry.entry_id}_room_{room_number}")},
            name=room_name,
            manufacturer=MANUFACTURER,
            model=model,
            via_device=(DOMAIN, entry.entry_id),
        )

    @property
    def native_value(self) -> float | None:
        """Return the current base temperature."""
        return self.coordinator.getData(REG_BASE_TEMPERATURE_1 + (self._room_number - 1))

    async def async_set_native_value(self, value: float) -> None:
        """Set the base temperature."""
        # Write to device
        success = await self.hass.async_add_executor_job(
            self.coordinator.client.write_room_base_temperature,
            self._room_number,
            value,
        )

        if success:
            # Update coordinator data immediately
            await self.coordinator.async_request_refresh()
