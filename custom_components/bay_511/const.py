"""Constants for Bay Area 511 Transit integration."""

from logging import Logger, getLogger

LOGGER: Logger = getLogger(__package__)

DOMAIN = "bay_511"
ATTRIBUTION = "Data provided by 511.org"

API_BASE_URL = "https://api.511.org/transit"
DEFAULT_UPDATE_INTERVAL = 60  # seconds

CONF_API_KEY = "api_key"
CONF_STOPS = "stops"
CONF_AGENCY = "agency"
CONF_STOP_CODE = "stop_code"
