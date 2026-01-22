"""DataUpdateCoordinator for BIC WRG."""
from __future__ import annotations

import logging
from datetime import timedelta
from typing import Any

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_HOST, CONF_PORT
from homeassistant.core import HomeAssistant
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
from .modbus import ModbusClient
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
        return self.config_entry.data.get(CONF_DEVICE_TYPE, DEVICE_TYPE_WGT) == DEVICE_TYPE_WGT

    async def async_write_register(self, register: int, value: int) -> None:
        success = await self.hass.async_add_executor_job(
            self.client.write_register, register, int(value)
        )

        if success:
            await self.async_request_refresh()

    async def async_write_room_register(self, base_register: int, roomt_number: int, value: int) -> None:
        await self.async_write_register(room_reg(base_register, roomt_number), value)


    # async def write_register(self, address: int, value: int) -> bool:
    #     """Write a register to the device."""
    #     return await self.hass.async_add_executor_job(
    #         self.client.write_register, address, value
    #     )

    def get_data(self, register: int|None, map: dict[int, Any]|None = None) -> Any:
        if register is None:
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

    def get_device(self) -> DeviceInfo:
        if self._device is None:
            model = MODEL_WGT if self.has_heating() else MODEL_WRT
            self._device = DeviceInfo(
                identifiers={(DOMAIN, self.config_entry.entry_id)},
                name=model,
                manufacturer=MANUFACTURER,
                model=model,
            )

        return self._device


    def get_room_device(self, room: int):
        if room not in self._room_devices:
            rooms = self.config_entry.data.get(CONF_ROOMS, [])

            self._room_devices[room] = DeviceInfo(
                identifiers={(DOMAIN, f"{self.config_entry.entry_id}_room_{room}")},
                name=rooms[room - 1]["name"],
                manufacturer=MANUFACTURER,
                model="Room Climate Control",
                via_device=(DOMAIN, self.config_entry.entry_id),
            )

        return self._room_devices[room]

