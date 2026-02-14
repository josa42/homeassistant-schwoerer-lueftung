"""Constants for the Schwörer Lüftung integration."""

DOMAIN = "schwoerer_lueftung"

# Configuration
CONF_HOST = "host"
CONF_ROOMS = "rooms"
CONF_DEVICE_TYPE = "device_type"
CONF_ENABLE_ALL_SENSORS_BY_DEFAULT = "enable_all_sensors_by_default"
CONF_HAS_GROUND_HEAT_EXCHANGER = "has_ground_heat_exchanger"

# Device types
DEVICE_TYPE_WGT = "wgt"  # With heating
DEVICE_TYPE_WRT = "wrt"  # Ventilation only

# Default values
DEFAULT_PORT = 502
DEFAULT_SCAN_INTERVAL = 30
DEFAULT_DEVICE_TYPE = DEVICE_TYPE_WGT

# Device information
MANUFACTURER = "Schwörer"
MODEL_WGT = "WGT"  # Heating system
MODEL_WRT = "WRT"  # Ventilation only
