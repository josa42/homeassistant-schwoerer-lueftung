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
        
        # Test read to verify communication
        await hass.async_add_executor_job(client.disconnect)
    except Exception as err:
        _LOGGER.error("Failed to connect: %s", err)
        raise CannotConnect from err
    
    return {"title": f"WRG {data[CONF_HOST]}"}


class ConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for BIC WRG."""

    VERSION = 1

    def __init__(self):
        """Initialize config flow."""
        self._host_data: dict[str, Any] = {}

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
            
            # Generate room data with number and name
            for i in range(1, num_rooms + 1):
                data[CONF_ROOMS].append({"number": i, "name": f"Room {i}"})
            
            info = {"title": f"WRG {self._host_data[CONF_HOST]}"}
            return self.async_create_entry(title=info["title"], data=data)
        
        # Build schema for number of rooms
        schema_dict = {
            vol.Required("num_rooms", default=0): vol.All(
                vol.Coerce(int), vol.Range(min=0, max=17)
            )
        }
        
        return self.async_show_form(
            step_id="rooms",
            data_schema=vol.Schema(schema_dict),
        )


class CannotConnect(HomeAssistantError):
    """Error to indicate we cannot connect."""
