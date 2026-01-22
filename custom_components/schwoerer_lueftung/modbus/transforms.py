"""Transform functions for Modbus register values."""
from __future__ import annotations

import logging

_LOGGER = logging.getLogger(__name__)


def to_temperature(value: int | None) -> float | None:
    """Convert register value to temperature in °C."""
    try:
        return int.from_bytes(value.to_bytes(2, 'big'), 'big', signed=True) / 10.0 if value is not None else None
    except Exception as err:
        _LOGGER.error("Error converting temperature value: %s", err)
        return None


def to_bool(value: int | None) -> bool | None:
    """Convert register value to bool."""
    return value == 1 if value is not None else None
