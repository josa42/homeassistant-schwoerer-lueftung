from __future__ import annotations

import logging
from datetime import timedelta
from typing import TYPE_CHECKING, Any

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_HOST
from homeassistant.core import HomeAssistant
from homeassistant.helpers import device_registry
from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed
from modbus_connection import ModbusError

from .const import (
    CONF_DEVICE_TYPE,
    CONF_HAS_GROUND_HEAT_EXCHANGER,
    CONF_ROOMS,
    DEFAULT_PORT,
    DEFAULT_SCAN_INTERVAL,
    DEVICE_TYPE_WGT,
    DOMAIN,
    MANUFACTURER,
    MODEL_WGT,
    MODEL_WRT,
)
from .device import SchwoererDevice, UpdateReport

if TYPE_CHECKING:
    from modbus_connection.model import Component

_LOGGER = logging.getLogger(__name__)

type SchwoererConfigEntry = ConfigEntry[Coordinator]


class Coordinator(DataUpdateCoordinator[UpdateReport]):
    """Poll the device and hand the report to the entities.

    The data is the poll's :class:`UpdateReport` rather than a value map:
    entities read their values straight off the device's typed attributes and
    use the report only to decide whether their own sub-system answered.
    """

    _device: DeviceInfo | None = None

    def __init__(
        self,
        hass: HomeAssistant,
        entry: SchwoererConfigEntry,
        device: SchwoererDevice,
    ) -> None:
        self._room_devices: dict[int, DeviceInfo] = {}
        self.device = device

        super().__init__(
            hass,
            _LOGGER,
            config_entry=entry,
            name=DOMAIN,
            update_interval=timedelta(seconds=DEFAULT_SCAN_INTERVAL),
        )

        self._failed: frozenset[str] = frozenset()

    def has_heating(self) -> bool:
        return self.get_device_type() == DEVICE_TYPE_WGT

    def has_ground_heat_exchanger(self) -> bool:
        return self.config_entry.data.get(CONF_HAS_GROUND_HEAT_EXCHANGER, False)

    def get_device_type(self) -> str:
        return self.config_entry.data.get(CONF_DEVICE_TYPE, DEVICE_TYPE_WGT)

    ############################################################################
    # Writing

    async def async_write(self, component: Component, field: str, value: Any) -> None:
        """Write one field and refresh, so the new value shows up at once."""
        try:
            await component.write(field, value)
        except ModbusError as err:
            raise UpdateFailed(f"Error writing {field}: {err}") from err

        await self.async_request_refresh()

    ############################################################################
    # Device registry

    def register_device(self) -> None:
        """Register the main device in the device registry."""
        device_registry.async_get(self.hass).async_get_or_create(
            config_entry_id=self.config_entry.entry_id, **self.get_device()
        )

    def get_device_identifier(self) -> tuple[str, str]:
        return (
            DOMAIN,
            f"{self.config_entry.data[CONF_HOST]}:{DEFAULT_PORT}",
        )

    def get_room_device_identifier(self, room_number: int) -> tuple[str, str]:
        return (
            DOMAIN,
            f"{self.config_entry.data[CONF_HOST]}:{DEFAULT_PORT}#{room_number}",
        )

    def get_device(self) -> DeviceInfo:
        if self._device is None:
            model = (
                MODEL_WGT if self.get_device_type() == DEVICE_TYPE_WGT else MODEL_WRT
            )
            self._device = DeviceInfo(
                identifiers={self.get_device_identifier()},
                name=model,
                manufacturer=MANUFACTURER,
                model=model,
            )

        return self._device

    def get_room(self, number: int) -> dict[str, Any] | None:
        rooms = self.config_entry.data.get(CONF_ROOMS, [])
        return next((room for room in rooms if room["number"] == number), None)

    def get_room_name(self, number: int) -> str | None:
        room = self.get_room(number)
        if room is not None:
            return room.get("name")
        return f"Room {number}"

    def get_room_device(self, room_number: int) -> DeviceInfo:
        if room_number not in self._room_devices:
            room_name = self.get_room_name(room_number)
            model = (
                MODEL_WGT if self.get_device_type() == DEVICE_TYPE_WGT else MODEL_WRT
            )

            self._room_devices[room_number] = DeviceInfo(
                identifiers={self.get_room_device_identifier(room_number)},
                name=f"{model} - {room_name}",
                manufacturer=MANUFACTURER,
                model=f"{model} - {room_name}",
                via_device=self.get_device_identifier(),
            )

        return self._room_devices[room_number]

    ############################################################################
    # Polling

    async def _async_update_data(self) -> UpdateReport:
        try:
            report = await self.device.async_update()
        except ModbusError as err:
            raise UpdateFailed(f"Error communicating with device: {err}") from err

        if not report.updated:
            errors = list(report.failed.values())
            raise UpdateFailed(
                f"No sub-system answered: {errors[0]}"
            ) from ExceptionGroup("every sub-system failed", errors)

        # Log a sub-system the first time it starts failing, not on every poll.
        for name in sorted(report.failed.keys() - self._failed):
            _LOGGER.warning("Failed to fetch %s: %s", name, report.failed[name])
        self._failed = frozenset(report.failed)

        return report
