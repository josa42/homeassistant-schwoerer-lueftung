"""Tests for transformation functions."""

import pytest

from custom_components.schwoerer_lueftung.modbus.transforms import to_temperature


class TestToTemperature:
    """Test temperature transformation function."""

    def test_positive_temperature(self):
        """Test positive temperature conversion."""
        # 250 = 25.0°C
        assert to_temperature(250) == 25.0

    def test_negative_temperature(self):
        """Test negative temperature conversion."""
        # -50 = -5.0°C (as signed 16-bit)
        assert to_temperature(65486) == -5.0

    def test_zero_temperature(self):
        """Test zero temperature."""
        assert to_temperature(0) == 0.0

    def test_none_input(self):
        """Test None input returns None."""
        assert to_temperature(None) is None

    def test_max_positive_temperature(self):
        """Test maximum positive temperature."""
        # 1000 = 100.0°C
        assert to_temperature(1000) == 100.0

    def test_min_negative_temperature(self):
        """Test minimum negative temperature."""
        # -500 = -50.0°C (as signed 16-bit: 65036)
        assert to_temperature(65036) == -50.0

    def test_small_positive_value(self):
        """Test small positive value."""
        # 1 = 0.1°C
        assert to_temperature(1) == 0.1

    def test_small_negative_value(self):
        """Test small negative value."""
        # -1 = -0.1°C (as signed 16-bit: 65535)
        assert to_temperature(65535) == -0.1

    def test_typical_room_temperature(self):
        """Test typical room temperature."""
        # 220 = 22.0°C
        assert to_temperature(220) == 22.0

    def test_typical_outdoor_temperature(self):
        """Test typical outdoor temperature."""
        # 150 = 15.0°C
        assert to_temperature(150) == 15.0
