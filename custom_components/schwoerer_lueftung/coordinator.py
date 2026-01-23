from __future__ import annotations

import logging
from datetime import timedelta
from typing import Any

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_HOST, CONF_PORT
from homeassistant.core import HomeAssistant
from homeassistant.helpers import device_registry
from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .const import (
    CONF_DEVICE_TYPE,
    CONF_ROOMS,
    CONF_SLAVE_ID,
    DEFAULT_SCAN_INTERVAL,
    DEVICE_TYPE_WGT,
    DOMAIN,
    MANUFACTURER,
    MODEL_WGT,
    MODEL_WRT,
)
from .modbus.client import ModbusClient
from .modbus.registers import REG_KEYS, room_reg

_LOGGER = logging.getLogger(__name__)


class Coordinator(DataUpdateCoordinator[dict[str, Any]]):
    _device: DeviceInfo | None = None
    _room_devices: dict[int, DeviceInfo] = {}

    def __init__(self, hass: HomeAssistant, entry: ConfigEntry) -> None:
        self.config_entry = entry
        self.client = ModbusClient(
            host=entry.data[CONF_HOST],
            port=entry.data[CONF_PORT],
            slave_id=entry.data[CONF_SLAVE_ID],
            device_type=entry.data.get(CONF_DEVICE_TYPE, DEVICE_TYPE_WGT),
        )

        super().__init__(
            hass,
            _LOGGER,
            name=DOMAIN,
            update_interval=timedelta(seconds=DEFAULT_SCAN_INTERVAL),
        )

    def has_heating(self) -> bool:
        return self.get_device_type() == DEVICE_TYPE_WGT

    def get_device_type(self) -> str:
        return self.config_entry.data.get(CONF_DEVICE_TYPE, DEVICE_TYPE_WGT)


    async def async_write_register(self, register: int, value: int) -> None:
        try:
          if not await self.hass.async_add_executor_job(self.client.connect):
              raise UpdateFailed("Failed to connect to device")

          success = await self.hass.async_add_executor_job(
              self.client.write_register, register, int(value)
          )

          if success:
              await self.async_request_refresh()

        except Exception as err:
            raise UpdateFailed(f"Error communicating with device: {err}") from err
        finally:
            await self.hass.async_add_executor_job(self.client.disconnect)

    async def async_write_room_register(self, base_register: int, roomt_number: int, value: int) -> None:
        await self.async_write_register(room_reg(base_register, roomt_number), value)

    def get_data(self, register: int|None, map: dict[int, Any]|None = None) -> Any:
        if self.data is None or register is None:
            return None

        try:
          key = REG_KEYS.get(register)
          if key is None:
            return None

          if not self.client.is_subscribed(register):
            self.client.subscribe(register)

          value = self.data.get(key)

          if map is not None and value is not None:
              return map[value]

          return value

        except Exception as err:
          _LOGGER.error(f"Error getting data for register {register}: {err}")
          return None

    def get_room_data(self, base_register: int, room_number: int, map: dict[int, Any]|None = None) -> Any:
        return self.get_data(room_reg(base_register, room_number), map)


    def register_device(self) -> None:
        device_registry.async_get(self.hass).async_get_or_create(
            config_entry_id=self.config_entry.entry_id,
            **self.get_device()
        )

    def get_device_identifier(self) -> tuple[str, str]:
        return (DOMAIN, f"{self.config_entry.data[CONF_HOST]}:{self.config_entry.data[CONF_PORT]}")

    def get_room_device_identifier(self, room_number) -> tuple[str, str]:
        return (DOMAIN,
                f"{self.config_entry.data[CONF_HOST]}:{self.config_entry.data[CONF_PORT]}#{room_number}")

    def get_device(self) -> DeviceInfo:
        if self._device is None:

            model=MODEL_WGT if self.get_device_type() == DEVICE_TYPE_WGT else MODEL_WRT
            self._device = DeviceInfo(
                identifiers={self.get_device_identifier()},
                name=model,
                manufacturer=MANUFACTURER,
                model=model,
            )

        return self._device

    def get_room_device(self, room_number: int):
        if room_number not in self._room_devices:
            rooms = self.config_entry.data.get(CONF_ROOMS, [])
            room_name = next((room["name"] for room in rooms if room['number'] == room_number), None)
            model=MODEL_WGT if self.get_device_type() == DEVICE_TYPE_WGT else MODEL_WRT

            self._room_devices[room_number] = DeviceInfo(
                identifiers={self.get_room_device_identifier(room_number)},
                name=f"{model} - {room_name}",
                manufacturer=MANUFACTURER,
                model=f"{model} - {room_name}",
                via_device=self.get_device_identifier(),
            )

            _LOGGER.debug(f"Created device info for room {room_number}: [ via_device: {self.config_entry.entry_id} ]")

        return self._room_devices[room_number]

    async def _async_update_data(self) -> dict[str, Any]:
        try:
            if not await self.hass.async_add_executor_job(self.client.connect):
                raise UpdateFailed("Failed to connect to device")

            return await self.hass.async_add_executor_job(self.client.read_data)

        except Exception as err:
            raise UpdateFailed(f"Error communicating with device: {err}") from err
        finally:
            await self.hass.async_add_executor_job(self.client.disconnect)

