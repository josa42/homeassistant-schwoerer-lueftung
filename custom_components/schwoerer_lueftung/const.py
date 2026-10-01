"""Constants for the Schwörer Lüftung integration."""

DOMAIN = "schwoerer_lueftung"

# Configuration
CONF_HOST = "host"
CONF_ROOMS = "rooms"
CONF_DEVICE_TYPE = "device_type"
CONF_HAS_GROUND_HEAT_EXCHANGER = "has_ground_heat_exchanger"

# Device types
DEVICE_TYPE_WGT = "wgt"  # With heating
DEVICE_TYPE_WRT = "wrt"  # Ventilation only

# Default values
DEFAULT_PORT = 502
# The device answers on a fixed station address, so it stays a constant rather
# than a config flow question. This is the address pymodbus defaulted to before
# the unit had to be named explicitly.
DEFAULT_UNIT_ID = 1
DEFAULT_SCAN_INTERVAL = 30
DEFAULT_DEVICE_TYPE = DEVICE_TYPE_WGT

# Device information
MANUFACTURER = "Schwörer"
MODEL_WGT = "WGT"  # Heating system
MODEL_WRT = "WRT"  # Ventilation only

# Writing
#
# The device needs time between register accesses, so queued writes are paced
# rather than issued as fast as the connection allows. A write is read back to
# confirm it landed, because a write the device acknowledges and then discards
# is the failure that made the 1.x write path unusable.
WRITE_SPACING = 0.2
WRITE_READBACK_DELAY = 0.1

# Retries are off for now, so a write is read back and a mismatch reported
# without anything being re-written. Verification assumes that reading a
# register back returns what was written to it, and that is unproven on the
# hardware: a register the firmware self-clears or normalises - the shock
# ventilation trigger is the obvious suspect - would turn every write to it
# into three and an error line. Observe first, then raise this to 2.
WRITE_READBACK_RETRIES = 0
