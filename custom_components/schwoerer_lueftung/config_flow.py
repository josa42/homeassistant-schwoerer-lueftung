"""Config flow for BIC WRG integration."""
from __future__ import annotations

import logging
from typing import Any

import voluptuous as vol
from homeassistant import config_entries
from homeassistant.const import CONF_HOST, CONF_PORT
from homeassistant.core import HomeAssistant
from homeassistant.data_entry_flow import FlowResult
from homeassistant.exceptions import HomeAssistantError
from homeassistant.helpers import translation

from .const import (
    CONF_ROOMS,
    CONF_SLAVE_ID,
    DEFAULT_PORT,
    DEFAULT_SLAVE_ID,
    DOMAIN,
)

_LOGGER = logging.getLogger(__name__)

STEP_USER_DATA_SCHEMA = vol.Schema(
    {
        vol.Required(CONF_HOST): str,
        vol.Optional(CONF_PORT, default=DEFAULT_PORT): int,
    }
)


async def validate_input(hass: HomeAssistant, data: dict[str, Any]) -> dict[str, Any]:
    """Validate the user input allows us to connect."""
    try:
        from .modbus_client import BicWrgModbusClient
    except ImportError as err:
        _LOGGER.error("Failed to import modbus client: %s", err)
        raise CannotConnect from err
    
    client = BicWrgModbusClient(
        data[CONF_HOST],
        data[CONF_PORT],
        DEFAULT_SLAVE_ID,
    )
    
    try:
        await hass.async_add_executor_job(client.connect)
        if not client.is_connected():
            raise CannotConnect
        
        # Try to detect room count (non-blocking, can fail gracefully)
        room_count = None
        try:
            room_count = await hass.async_add_executor_job(client.detect_room_count)
        except Exception as detect_err:
            _LOGGER.warning("Room count detection failed: %s", detect_err)
        
        await hass.async_add_executor_job(client.disconnect)
        
        result = {"title": f"WRG {data[CONF_HOST]}"}
        if room_count is not None:
            result["detected_rooms"] = room_count
        
        return result
    except CannotConnect:
        raise
    except Exception as err:
        _LOGGER.error("Failed to connect: %s", err)
        raise CannotConnect from err


class ConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for BIC WRG."""

    VERSION = 1

    def __init__(self):
        """Initialize config flow."""
        self._host_data: dict[str, Any] = {}
        self._detected_rooms: int | None = None

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Handle the initial step."""
        errors: dict[str, str] = {}
        
        if user_input is not None:
            try:
                info = await validate_input(self.hass, user_input)
            except CannotConnect:
                errors["base"] = "cannot_connect"
            except Exception:  # pylint: disable=broad-except
                _LOGGER.exception("Unexpected exception")
                errors["base"] = "unknown"
            else:
                await self.async_set_unique_id(user_input[CONF_HOST])
                self._abort_if_unique_id_configured()
                self._host_data = user_input
                self._detected_rooms = info.get("detected_rooms")
                
                # If room count was auto-detected, skip the room config step
                if self._detected_rooms is not None:
                    return await self.async_step_rooms(user_input={"num_rooms": self._detected_rooms})
                
                return await self.async_step_rooms()
        
        return self.async_show_form(
            step_id="user", data_schema=STEP_USER_DATA_SCHEMA, errors=errors
        )

    async def async_step_rooms(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Handle room configuration."""
        if user_input is not None:
            num_rooms = user_input.get("num_rooms", 0)
            
            # Store room configuration with default slave ID
            data = {**self._host_data, CONF_SLAVE_ID: DEFAULT_SLAVE_ID, CONF_ROOMS: []}
            
            # Get translations to use the correct room prefix
            translations = await translation.async_get_translations(
                self.hass, self.hass.config.language, "entity", {DOMAIN}
            )
            room_key = f"component.{DOMAIN}.entity.device.room.name"
            room_prefix = translations.get(room_key, "Room")
            
            for i in range(1, num_rooms + 1):
                data[CONF_ROOMS].append({"number": i, "name": f"{room_prefix} {i}"})
            
            info = {"title": f"WRG {self._host_data[CONF_HOST]}"}
            return self.async_create_entry(title=info["title"], data=data)
        
        # Use detected room count as default, or 1 if not detected
        default_rooms = self._detected_rooms if self._detected_rooms is not None else 1
        
        # Build schema for number of rooms with auto-detected value
        schema_dict = {
            vol.Required("num_rooms", default=default_rooms): vol.All(
                vol.Coerce(int), vol.Range(min=1, max=17)
            )
        }
        
        # Add description if rooms were auto-detected
        description_placeholders = {}
        if self._detected_rooms is not None:
            description_placeholders["detected_rooms"] = str(self._detected_rooms)
        
        return self.async_show_form(
            step_id="rooms",
            data_schema=vol.Schema(schema_dict),
            description_placeholders=description_placeholders,
        )


class CannotConnect(HomeAssistantError):
    """Error to indicate we cannot connect."""
