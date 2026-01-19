"""Test the Schwörer Lüftung integration initialisation."""
from unittest.mock import MagicMock, patch

import pytest
from homeassistant.config_entries import ConfigEntryState
from homeassistant.const import CONF_HOST, CONF_PORT
from homeassistant.core import HomeAssistant
from pytest_homeassistant_custom_component.common import MockConfigEntry

from custom_components.schwoerer_lueftung.const import CONF_SLAVE_ID, DOMAIN


@pytest.fixture
def mock_modbus_client():
    """Mock the Modbus client."""
    with patch(
        "custom_components.schwoerer_lueftung.coordinator.ModbusClient"
    ) as mock_client:
        client_instance = MagicMock()
        client_instance.connect.return_value = True
        client_instance.is_connected.return_value = True
        client_instance.read_data.return_value = {}
        mock_client.return_value = client_instance
        yield mock_client


async def test_setup_entry(hass: HomeAssistant, mock_modbus_client) -> None:
    """Test setting up the integration."""
    entry = MockConfigEntry(
        domain=DOMAIN,
        data={
            CONF_HOST: "192.168.1.100",
            CONF_PORT: 502,
            CONF_SLAVE_ID: 1,
        },
    )
    entry.add_to_hass(hass)

    assert await hass.config_entries.async_setup(entry.entry_id)
    await hass.async_block_till_done()

    assert entry.state == ConfigEntryState.LOADED
    assert DOMAIN in hass.data


async def test_unload_entry(hass: HomeAssistant, mock_modbus_client) -> None:
    """Test unloading the integration."""
    entry = MockConfigEntry(
        domain=DOMAIN,
        data={
            CONF_HOST: "192.168.1.100",
            CONF_PORT: 502,
            CONF_SLAVE_ID: 1,
        },
    )
    entry.add_to_hass(hass)

    assert await hass.config_entries.async_setup(entry.entry_id)
    await hass.async_block_till_done()

    assert await hass.config_entries.async_unload(entry.entry_id)
    await hass.async_block_till_done()

    assert entry.state == ConfigEntryState.NOT_LOADED
    assert entry.entry_id not in hass.data[DOMAIN]
