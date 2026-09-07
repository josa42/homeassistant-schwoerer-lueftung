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
