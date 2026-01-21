"""DataUpdateCoordinator for BIC WRG."""
from __future__ import annotations

from datetime import timedelta
import logging
from typing import Any

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_HOST, CONF_PORT
from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .const import (
    CONF_DEVICE_TYPE,
    CONF_SLAVE_ID,
    CONF_ROOMS,
    DEFAULT_SCAN_INTERVAL,
    DEVICE_TYPE_WGT,
    DOMAIN,
)
from .modbus_client import BicWrgModbusClient

_LOGGER = logging.getLogger(__name__)


class BicWrgCoordinator(DataUpdateCoordinator[dict[str, Any]]):
    """Class to manage fetching WRG data."""

    def __init__(self, hass: HomeAssistant, entry: ConfigEntry) -> None:
        """Initialize."""
        self.config_entry = entry
        self.client = BicWrgModbusClient(
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
        """Check if device has heating capabilities (WGT)."""
        return self.config_entry.data.get(CONF_DEVICE_TYPE, DEVICE_TYPE_WGT) == DEVICE_TYPE_WGT

    async def write_register(self, address: int, value: int) -> bool:
        """Write a register to the device."""
        return await self.hass.async_add_executor_job(
            self.client.write_register, address, value
        )

    async def write_room_heating_enable(self, room_number: int, enabled: int) -> bool:
        """Write room heating enable."""
        return await self.hass.async_add_executor_job(
            self.client.write_room_heating_enable, room_number, enabled
        )

    async def _async_update_data(self) -> dict[str, Any]:
        """Fetch data from WRG device."""
        try:
            if not await self.hass.async_add_executor_job(self.client.connect):
                raise UpdateFailed("Failed to connect to device")
            
            data = await self.hass.async_add_executor_job(self.client.read_data)
            
            # For now, return empty dict if no data (placeholder until registers are mapped)
            # Remove this check once actual register reading is implemented
            if data is None:
                raise UpdateFailed("Failed to read data from device")
            
            return data
        except Exception as err:
            raise UpdateFailed(f"Error communicating with device: {err}") from err
        finally:
            await self.hass.async_add_executor_job(self.client.disconnect)
