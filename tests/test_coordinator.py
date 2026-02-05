"""Tests for Coordinator."""

from unittest.mock import MagicMock, patch

import pytest
from homeassistant.const import CONF_HOST, CONF_PORT
from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import UpdateFailed
from pytest_homeassistant_custom_component.common import MockConfigEntry

from custom_components.schwoerer_lueftung.const import (
    CONF_DEVICE_TYPE,
    CONF_ROOMS,
    CONF_SLAVE_ID,
    DEVICE_TYPE_WGT,
    DEVICE_TYPE_WRT,
    DOMAIN,
)
from custom_components.schwoerer_lueftung.coordinator import Coordinator


@pytest.fixture
def mock_modbus_client():
    """Mock Modbus client."""
    with patch(
        "custom_components.schwoerer_lueftung.coordinator.ModbusClient"
    ) as mock:
        client_instance = MagicMock()
        client_instance.connect.return_value = True
        client_instance.is_subscribed.return_value = False
        client_instance.read_data.return_value = {
            "current_fan_level": 2,
            "temp_t10_outdoor": 220,
        }
        mock.return_value = client_instance
        yield mock, client_instance


@pytest.fixture
def config_entry_wgt():
    """Mock config entry for WGT device."""
    return MockConfigEntry(
        domain=DOMAIN,
        data={
            CONF_HOST: "192.168.1.100",
            CONF_PORT: 502,
            CONF_SLAVE_ID: 1,
            CONF_DEVICE_TYPE: DEVICE_TYPE_WGT,
            CONF_ROOMS: [
                {"number": 1, "name": "Living Room"},
                {"number": 2, "name": "Bedroom"},
            ],
        },
    )


@pytest.fixture
def config_entry_wrt():
    """Mock config entry for WRT device."""
    return MockConfigEntry(
        domain=DOMAIN,
        data={
            CONF_HOST: "192.168.1.100",
            CONF_PORT: 502,
            CONF_SLAVE_ID: 1,
            CONF_DEVICE_TYPE: DEVICE_TYPE_WRT,
        },
    )


class TestCoordinatorInit:
    """Test Coordinator initialization."""

    async def test_init_creates_client(self, hass: HomeAssistant, mock_modbus_client, config_entry_wgt):
        """Test coordinator initialization creates modbus client."""
        coordinator = Coordinator(hass, config_entry_wgt)
        assert coordinator.client is not None


class TestCoordinatorDataUpdate:
    """Test Coordinator data update cycle."""

    async def test_update_data_success(
        self, hass: HomeAssistant, mock_modbus_client, config_entry_wgt
    ):
        """Test successful data update."""
        _, client_instance = mock_modbus_client
        coordinator = Coordinator(hass, config_entry_wgt)

        result = await coordinator._async_update_data()

        assert result is not None
        assert "current_fan_level" in result
        assert result["current_fan_level"] == 2
        client_instance.connect.assert_called()
        client_instance.read_data.assert_called()
        client_instance.disconnect.assert_called()

    async def test_update_data_connection_failure(
        self, hass: HomeAssistant, mock_modbus_client, config_entry_wgt
    ):
        """Test data update with connection failure."""
        _, client_instance = mock_modbus_client
        client_instance.connect.return_value = False

        coordinator = Coordinator(hass, config_entry_wgt)

        with pytest.raises(UpdateFailed, match="Failed to connect to device"):
            await coordinator._async_update_data()

    async def test_update_data_read_exception(
        self, hass: HomeAssistant, mock_modbus_client, config_entry_wgt
    ):
        """Test data update with read exception."""
        _, client_instance = mock_modbus_client
        client_instance.read_data.side_effect = Exception("Read error")

        coordinator = Coordinator(hass, config_entry_wgt)

        with pytest.raises(UpdateFailed, match="Error communicating with device"):
            await coordinator._async_update_data()

        # Ensure disconnect is still called
        client_instance.disconnect.assert_called()


class TestCoordinatorDataRetrieval:
    """Test Coordinator data retrieval methods."""

    async def test_get_data_with_value(
        self, hass: HomeAssistant, mock_modbus_client, config_entry_wgt
    ):
        """Test get_data returns value when available."""
        coordinator = Coordinator(hass, config_entry_wgt)
        coordinator.data = {"current_fan_level": 2}

        result = coordinator.get_data(102)  # REG_CURRENT_FAN_LEVEL

        assert result == 2

    async def test_get_data_none_when_no_data(
        self, hass: HomeAssistant, mock_modbus_client, config_entry_wgt
    ):
        """Test get_data returns None when data not available."""
        coordinator = Coordinator(hass, config_entry_wgt)
        coordinator.data = None

        result = coordinator.get_data(102)

        assert result is None

    async def test_get_data_with_map(
        self, hass: HomeAssistant, mock_modbus_client, config_entry_wgt
    ):
        """Test get_data with mapping."""
        coordinator = Coordinator(hass, config_entry_wgt)
        coordinator.data = {"current_fan_level": 2}

        mapping = {0: "off", 1: "level_1", 2: "level_2"}
        result = coordinator.get_data(102, mapping)

        assert result == "level_2"
