"""The BIC WRG integration."""
from __future__ import annotations

import logging
from typing import Any

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import Platform
from homeassistant.core import HomeAssistant
from homeassistant.exceptions import ConfigEntryNotReady

from .const import CONF_DEVICE_TYPE, DEVICE_TYPE_WGT, DOMAIN
from .coordinator import BicWrgCoordinator

_LOGGER = logging.getLogger(__name__)

PLATFORMS: list[Platform] = [
    Platform.BINARY_SENSOR,
    Platform.CLIMATE,
    Platform.NUMBER,
    Platform.SELECT,
    Platform.SENSOR,
    Platform.SWITCH,
]


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up BIC WRG from a config entry."""
    coordinator = BicWrgCoordinator(hass, entry)
    
    try:
        await coordinator.async_config_entry_first_refresh()
    except Exception as err:
        raise ConfigEntryNotReady(f"Failed to connect to device: {err}") from err
    
    hass.data.setdefault(DOMAIN, {})
    hass.data[DOMAIN][entry.entry_id] = coordinator
    
    # Load platforms based on device type
    device_type = entry.data.get(CONF_DEVICE_TYPE, DEVICE_TYPE_WGT)
    platforms_to_load = PLATFORMS.copy()
    
    # For WRT (ventilation only), exclude climate platform
    if device_type != DEVICE_TYPE_WGT:
        platforms_to_load = [p for p in platforms_to_load if p != Platform.CLIMATE]
    
    await hass.config_entries.async_forward_entry_setups(entry, platforms_to_load)
    
    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    # Determine which platforms were loaded
    device_type = entry.data.get(CONF_DEVICE_TYPE, DEVICE_TYPE_WGT)
    platforms_to_unload = PLATFORMS.copy()
    
    if device_type != DEVICE_TYPE_WGT:
        platforms_to_unload = [p for p in platforms_to_unload if p != Platform.CLIMATE]
    
    if unload_ok := await hass.config_entries.async_unload_platforms(entry, platforms_to_unload):
        hass.data[DOMAIN].pop(entry.entry_id)
    
    return unload_ok
