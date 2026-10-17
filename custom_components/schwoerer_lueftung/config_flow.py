"""Config flow for Schwörer Lüftung integration."""

from __future__ import annotations

import logging
from typing import Any

import voluptuous as vol
from homeassistant import config_entries
from homeassistant.components.modbus import async_get_temporary_unit
from homeassistant.const import CONF_HOST
from homeassistant.core import HomeAssistant
from homeassistant.exceptions import HomeAssistantError
from homeassistant.helpers import translation
from homeassistant.helpers.selector import (
    NumberSelector,
    NumberSelectorConfig,
    NumberSelectorMode,
    SelectOptionDict,
    SelectSelector,
    SelectSelectorConfig,
    SelectSelectorMode,
)
from modbus_connection import ModbusError, ModbusExceptionError, ModbusTcpParams

from .const import (
    CONF_DEVICE_TYPE,
    CONF_HAS_GROUND_HEAT_EXCHANGER,
    CONF_ROOMS,
    DEFAULT_DEVICE_TYPE,
    DEFAULT_PORT,
    DEFAULT_UNIT_ID,
    DEVICE_TYPE_WGT,
    DEVICE_TYPE_WRT,
    DOMAIN,
    MODEL_WGT,
    MODEL_WRT,
)
from .device.components import Ventilation

_LOGGER = logging.getLogger(__name__)

# The block at 100-104 is the fan control every firmware serves. Reading the
# whole of Ventilation instead would fail the flow on a firmware that lacks one
# of its optional registers, which the device layer would otherwise skip.
PROBE_FIELDS = (
    "operation_mode",
    "fan_speed",
    "current_fan_level",
    "linear_fan_power",
    "fan_override",
)


async def validate_input(hass: HomeAssistant, data: dict[str, Any]) -> dict[str, Any]:
    """Check the device answers before creating the entry.

    The flow has no config entry yet to tie a connection to, so it borrows a
    unit for the duration of the context. A connection an entry already holds
    is shared and stays up; one opened here closes on exit.
    """
    params = ModbusTcpParams(host=data[CONF_HOST], port=DEFAULT_PORT)

    try:
        async with async_get_temporary_unit(hass, params, DEFAULT_UNIT_ID) as unit:
            probe = Ventilation(unit)
            probe.restrict_fields(PROBE_FIELDS)
            await probe.async_update()
    except ModbusExceptionError as err:
        # The device answered, so the link works; it refused the registers.
        _LOGGER.error("The device refused the probe read: %s", err)
        raise DeviceRefused from err
    except ModbusError as err:
        _LOGGER.error("Failed to reach the device: %s", err)
        raise CannotConnect from err
    except HomeAssistantError:
        # The device is already in use over different link settings.
        raise

    model = MODEL_WGT if data[CONF_DEVICE_TYPE] == DEVICE_TYPE_WGT else MODEL_WRT

    return {"title": f"{model} {data[CONF_HOST]}"}


class ConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    VERSION = 1

    async def _get_schema(self) -> vol.Schema:
        """Build schema with translated device type options."""
        translations = await translation.async_get_translations(
            self.hass, self.hass.config.language, "selector", {DOMAIN}
        )

        wgt_key = (
            f"component.{DOMAIN}.selector.{CONF_DEVICE_TYPE}.options.{DEVICE_TYPE_WGT}"
        )
        wrt_key = (
            f"component.{DOMAIN}.selector.{CONF_DEVICE_TYPE}.options.{DEVICE_TYPE_WRT}"
        )

        wgt_label = translations.get(wgt_key, "WGT (with heating)")
        wrt_label = translations.get(wrt_key, "WRT (ventilation only)")

        return vol.Schema(
            {
                vol.Required(CONF_HOST): str,
                vol.Required(
                    CONF_DEVICE_TYPE, default=DEFAULT_DEVICE_TYPE
                ): SelectSelector(
                    SelectSelectorConfig(
                        options=[
                            SelectOptionDict(value=DEVICE_TYPE_WGT, label=wgt_label),
                            SelectOptionDict(value=DEVICE_TYPE_WRT, label=wrt_label),
                        ],
                        mode=SelectSelectorMode.DROPDOWN,
                    )
                ),
                vol.Required(CONF_HAS_GROUND_HEAT_EXCHANGER, default=False): bool,
                vol.Required(CONF_ROOMS, default=1): NumberSelector(
                    NumberSelectorConfig(
                        min=1,
                        max=17,
                        step=1,
                        mode=NumberSelectorMode.BOX,
                    )
                ),
            }
        )

    async def async_step_user(self, user_input: dict[str, Any] | None = None):
        """Handle the initial step."""
        errors: dict[str, str] = {}

        if user_input is not None:
            try:
                info = await validate_input(self.hass, user_input)
            except CannotConnect:
                errors["base"] = "cannot_connect"
            except DeviceRefused:
                errors["base"] = "device_refused"
            except Exception:  # pylint: disable=broad-except
                _LOGGER.exception("Unexpected exception")
                errors["base"] = "unknown"
            else:
                await self.async_set_unique_id(user_input[CONF_HOST])
                self._abort_if_unique_id_configured()

                num_rooms = user_input[CONF_ROOMS]

                # Store configuration with default slave ID
                data = {
                    CONF_HOST: user_input[CONF_HOST],
                    CONF_DEVICE_TYPE: user_input[CONF_DEVICE_TYPE],
                    CONF_ROOMS: [],
                    CONF_HAS_GROUND_HEAT_EXCHANGER: user_input[
                        CONF_HAS_GROUND_HEAT_EXCHANGER
                    ],
                }

                # Get translations to use the correct room prefix
                translations = await translation.async_get_translations(
                    self.hass, self.hass.config.language, "entity", {DOMAIN}
                )
                room_key = f"component.{DOMAIN}.entity.device.room.name"
                room_prefix = translations.get(room_key, "Room")

                for i in range(1, int(num_rooms) + 1):
                    data[CONF_ROOMS].append({"number": i, "name": f"{room_prefix} {i}"})

                return self.async_create_entry(title=info["title"], data=data)

        schema = await self._get_schema()
        return self.async_show_form(step_id="user", data_schema=schema, errors=errors)


class CannotConnect(HomeAssistantError):
    """Error to indicate we cannot connect."""


class DeviceRefused(HomeAssistantError):
    """Error to indicate the device answered but refused the registers."""
