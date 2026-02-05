"""Tests for Modbus client."""

from unittest.mock import MagicMock, Mock, patch

import pytest

from custom_components.schwoerer_lueftung.modbus.client import ModbusClient


@pytest.fixture
def mock_pymodbus_client():
    """Mock pymodbus ModbusTcpClient."""
    with patch("custom_components.schwoerer_lueftung.modbus.client.ModbusTcpClient") as mock:
        yield mock


class TestModbusClientInit:
    """Test ModbusClient initialization."""

    def test_init_with_defaults(self, mock_pymodbus_client):
        """Test initialization with default parameters."""
        client = ModbusClient("192.168.1.100", 502, 1)
        
        assert client.host == "192.168.1.100"
        assert client.port == 502
        assert client.slave_id == 1
        assert client.device_type == "wgt"

    def test_init_with_wrt_device(self, mock_pymodbus_client):
        """Test initialization with WRT device type."""
        client = ModbusClient("192.168.1.100", 502, 1, device_type="wrt")
        
        assert client.device_type == "wrt"


class TestModbusClientConnection:
    """Test ModbusClient connection management."""

    def test_connect_success(self, mock_pymodbus_client):
        """Test successful connection."""
        mock_instance = MagicMock()
        mock_instance.connect.return_value = True
        mock_pymodbus_client.return_value = mock_instance

        client = ModbusClient("192.168.1.100", 502, 1)
        result = client.connect()

        assert result is True
        mock_instance.connect.assert_called_once()

    def test_connect_failure(self, mock_pymodbus_client):
        """Test connection failure."""
        mock_instance = MagicMock()
        mock_instance.connect.return_value = False
        mock_pymodbus_client.return_value = mock_instance

        client = ModbusClient("192.168.1.100", 502, 1)
        result = client.connect()

        assert result is False

    def test_connect_exception(self, mock_pymodbus_client):
        """Test connection with exception."""
        mock_instance = MagicMock()
        mock_instance.connect.side_effect = Exception("Connection error")
        mock_pymodbus_client.return_value = mock_instance

        client = ModbusClient("192.168.1.100", 502, 1)
        
        with pytest.raises(Exception):
            client.connect()

    def test_disconnect(self, mock_pymodbus_client):
        """Test disconnect."""
        mock_instance = MagicMock()
        mock_pymodbus_client.return_value = mock_instance

        client = ModbusClient("192.168.1.100", 502, 1)
        client.disconnect()

        mock_instance.close.assert_called_once()

    def test_is_connected_true(self, mock_pymodbus_client):
        """Test is_connected returns True when connected."""
        mock_instance = MagicMock()
        mock_instance.is_socket_open.return_value = True
        mock_pymodbus_client.return_value = mock_instance

        client = ModbusClient("192.168.1.100", 502, 1)
        assert client.is_connected() is True

    def test_is_connected_false(self, mock_pymodbus_client):
        """Test is_connected returns False when not connected."""
        mock_instance = MagicMock()
        mock_instance.is_socket_open.return_value = False
        mock_pymodbus_client.return_value = mock_instance

        client = ModbusClient("192.168.1.100", 502, 1)
        assert client.is_connected() is False


class TestModbusClientSubscription:
    """Test ModbusClient register subscription."""

    def test_subscribe_single_register(self, mock_pymodbus_client):
        """Test subscribing to a single register."""
        client = ModbusClient("192.168.1.100", 502, 1)
        client.subscribe(100)

        assert client.is_subscribed(100) is True

    def test_subscribe_multiple_registers(self, mock_pymodbus_client):
        """Test subscribing to multiple registers."""
        client = ModbusClient("192.168.1.100", 502, 1)
        client.subscribe(100)
        client.subscribe(101)
        client.subscribe(102)

        assert client.is_subscribed(100) is True
        assert client.is_subscribed(101) is True
        assert client.is_subscribed(102) is True

    def test_is_subscribed_false(self, mock_pymodbus_client):
        """Test is_subscribed returns False for unsubscribed register."""
        mock_instance = MagicMock()
        mock_pymodbus_client.return_value = mock_instance
        
        client = ModbusClient("192.168.1.100", 502, 1)
        assert client.is_subscribed(999) is False


class TestModbusClientRead:
    """Test ModbusClient read operations."""

    def test_read_registers_success(self, mock_pymodbus_client):
        """Test successful register read."""
        mock_instance = MagicMock()
        mock_response = Mock()
        mock_response.isError.return_value = False
        mock_response.registers = [100, 200, 300]
        mock_instance.read_holding_registers.return_value = mock_response
        mock_pymodbus_client.return_value = mock_instance

        client = ModbusClient("192.168.1.100", 502, 1)
        result = client.read_registers(100, 3)

        assert result == [100, 200, 300]
        mock_instance.read_holding_registers.assert_called_once_with(address=100, count=3)

    def test_read_registers_error(self, mock_pymodbus_client):
        """Test register read with error response."""
        mock_instance = MagicMock()
        mock_response = Mock()
        mock_response.isError.return_value = True
        mock_instance.read_holding_registers.return_value = mock_response
        mock_pymodbus_client.return_value = mock_instance

        client = ModbusClient("192.168.1.100", 502, 1)
        result = client.read_registers(100, 3)

        assert result is None

    def test_read_registers_exception(self, mock_pymodbus_client):
        """Test register read with exception."""
        mock_instance = MagicMock()
        mock_instance.read_holding_registers.side_effect = Exception("Read error")
        mock_pymodbus_client.return_value = mock_instance

        client = ModbusClient("192.168.1.100", 502, 1)
        result = client.read_registers(100, 3)

        assert result is None


class TestModbusClientWrite:
    """Test ModbusClient write operations."""

    def test_write_register_success(self, mock_pymodbus_client):
        """Test successful register write."""
        mock_instance = MagicMock()
        mock_response = Mock()
        mock_response.isError.return_value = False
        mock_instance.write_registers.return_value = mock_response
        mock_pymodbus_client.return_value = mock_instance

        client = ModbusClient("192.168.1.100", 502, 1)
        result = client.write_register(100, 250)

        assert result is True
        mock_instance.write_registers.assert_called_once_with(address=100, values=[250])

    def test_write_register_error(self, mock_pymodbus_client):
        """Test register write with error response."""
        mock_instance = MagicMock()
        mock_response = Mock()
        mock_response.isError.return_value = True
        mock_instance.write_registers.return_value = mock_response
        mock_pymodbus_client.return_value = mock_instance

        client = ModbusClient("192.168.1.100", 502, 1)
        result = client.write_register(100, 250)

        assert result is False

    def test_write_register_exception(self, mock_pymodbus_client):
        """Test register write with exception."""
        mock_instance = MagicMock()
        mock_instance.write_registers.side_effect = Exception("Write error")
        mock_pymodbus_client.return_value = mock_instance

        client = ModbusClient("192.168.1.100", 502, 1)
        result = client.write_register(100, 250)

        assert result is False


class TestModbusClientReadData:
    """Test ModbusClient read_data operation."""

    def test_read_data_empty_subscriptions(self, mock_pymodbus_client):
        """Test read_data with no subscriptions."""
        mock_instance = MagicMock()
        mock_pymodbus_client.return_value = mock_instance
        
        client = ModbusClient("192.168.1.100", 502, 1)
        result = client.read_data()

        assert result == {}
