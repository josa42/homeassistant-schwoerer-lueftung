"""Tests for register helper functions."""

import pytest

from custom_components.schwoerer_lueftung.modbus.registers import room_reg


class TestRoomReg:
    """Test room register calculation function."""

    def test_room_1(self):
        """Test register calculation for room 1."""
        base_register = 400
        assert room_reg(base_register, 1) == 400

    def test_room_2(self):
        """Test register calculation for room 2."""
        base_register = 400
        assert room_reg(base_register, 2) == 401

    def test_room_17(self):
        """Test register calculation for room 17."""
        base_register = 400
        assert room_reg(base_register, 17) == 416

    def test_room_10(self):
        """Test register calculation for room 10."""
        base_register = 400
        assert room_reg(base_register, 10) == 409

    def test_different_base_register(self):
        """Test with different base register."""
        base_register = 500
        assert room_reg(base_register, 5) == 504

    def test_invalid_room_number_zero(self):
        """Test that room number 0 raises ValueError."""
        with pytest.raises(ValueError, match="Room number must be between 1 and 17"):
            room_reg(400, 0)

    def test_invalid_room_number_negative(self):
        """Test that negative room number raises ValueError."""
        with pytest.raises(ValueError, match="Room number must be between 1 and 17"):
            room_reg(400, -1)

    def test_invalid_room_number_too_high(self):
        """Test that room number > 17 raises ValueError."""
        with pytest.raises(ValueError, match="Room number must be between 1 and 17"):
            room_reg(400, 18)

    def test_invalid_room_number_way_too_high(self):
        """Test that room number >> 17 raises ValueError."""
        with pytest.raises(ValueError, match="Room number must be between 1 and 17"):
            room_reg(400, 100)
